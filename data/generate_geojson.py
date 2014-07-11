#!/usr/bin/env python
'''Munge Natural Earth GeoJSON into a format comparea likes.

Usage:
    ogr2ogr -f GeoJSON countries.geo.json ne_50m_admin_0_countries_lakes.shp
    ./generate_geojson.py countries.geo.json > comparea.geo.json
'''

import json
import sys
import os
from data import geojson_util
from data import country_codes


_descs = None
def get_description(code):
    global _descs
    if not _descs:
        p = os.path.join(os.path.dirname(__file__), 'descriptions.json')
        _descs = json.load(file(p))
    return _descs[code]


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
    out['id'] = iso3
    out_props['name'] = props['name']
    out_props['population'] = props['pop_est']
    out_props['population_year'] = '???'
    out_props['area_km2'] = geojson_util.get_area_of_feature(country) / 1e6
    out_props['description'] = get_description(iso3)
    wiki_url = country_codes.iso3_to_wikipedia_url(iso3)
    if not wiki_url:
        raise ValueError('Unable to get wikipedia link for %s = %s\n' % (iso3, props['name']))
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
