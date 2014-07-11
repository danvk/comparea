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


def process_province(province):
    assert province['type'] == 'Feature'
    props = province['properties']
    out_props = {}
    out = {
        'type': province['type'],
        'geometry': province['geometry'],
        'properties': out_props
    }

    short_admin = 'USA' if props['iso_a2'] == 'US' else props['admin']
    code = props['code_hasc'].replace('.', '_')
    out['id'] = code
    out_props['name'] = '%s (%s)' % (props['name'], short_admin)
    out_props['population'] = -1
    out_props['population_year'] = '???'
    out_props['area_km2'] = geojson_util.get_area_of_feature(province) / 1e6
    out_props['description'] = 'A nice place'
    wiki_url = props['wikipedia']
    if wiki_url:
        out_props['wikipedia_url'] = wiki_url
    else:
        out_props['wikipedia_url'] = '#'

    return out



def process_features(geojson, fn):
    features = []
    for feature in geojson['features']:
        features.append(fn(feature))

    return { 'type': 'FeatureCollection', 'features': features }


def run(args):
    assert len(args) == 3
    countries_geojson = json.load(file(args[1]))
    assert countries_geojson['type'] == 'FeatureCollection'
    country_features = process_features(countries_geojson, process_country)
    geojson_util.check_feature_collection(country_features)

    provinces_geojson = json.load(file(args[2]))
    assert provinces_geojson['type'] == 'FeatureCollection'
    province_features = process_features(provinces_geojson, process_province)
    geojson_util.check_feature_collection(province_features)

    comparea_features = country_features
    comparea_features['features'] += province_features['features']

    print json.dumps(comparea_features)


if __name__ == '__main__':
    run(sys.argv)
