#!/usr/bin/env python
'''Munge Natural Earth GeoJSON into a format comparea likes.

Usage:
    ogr2ogr -f GeoJSON countries.geo.json ne_50m_admin_0_countries_lakes.shp
    ./generate_geojson.py countries.geo.json > comparea.geo.json
'''

import json
import sys
from comparea import geojson_util
from data import country_codes


def process_country(country):
    assert country['type'] == 'Feature'
    props = country['properties']
    out_props = {}
    out = {
        'type': country['type'],
        'geometry': country['geometry'],
        'properties': out_props
    }

    iso3 = props['su_a3']
    out_props['id'] = iso3
    out_props['name'] = props['name']
    out_props['pop'] = props['pop_est']
    out_props['pop_year'] = '???'
    out_props['area_km2'] = 1000
    out_props['description'] = 'A nice place!'
    wiki_url = country_codes.iso3_to_wikipedia_url(iso3)
    if not wiki_url:
        sys.stderr.write('Unable to get wikipedia link for %s = %s\n' % (iso3, props['name']))
    out_props['wikipedia_url'] = wiki_url
    return out


def process_countries(geojson):
    features = []
    for feature in geojson['features']:
        features.append(process_country(feature))

    return { 'type': 'FeatureCollection', 'features': features }


def run(args):
    assert len(args) == 2
    geojson = json.load(file(args[1]))
    assert geojson['type'] == 'FeatureCollection'
    comparea_features = process_countries(geojson)
    geojson_util.check_feature_collection(comparea_features)

    print json.dumps(comparea_features)


if __name__ == '__main__':
    run(sys.argv)
