#!/usr/bin/env python
'''Summarize Natural Earth GeoJSON.
'''

import json
import sys
import geojson_util

fields = ['index', 'su_a3', 'name', 'name_long', 'pop_est', 'pop_year', 'continent', 'region_un', 'subregion', 'area_km2', 'bbox_area_km2', 'solidity']


def fmt(x):
    if type(x) == int or type(x) == float:
        return str(x)
    else:
        return x


def process_country(country):
    assert country['type'] == 'Feature'
    props = country['properties']
    print ('\t'.join([fmt(props[f]) for f in fields])).encode('utf-8')


def calculate_properties(feature):
    area_km2 = geojson_util.get_area_of_feature(feature) / 1e6
    try:
        bbox_area_km2 = geojson_util.get_convex_area_of_feature(feature) / 1e6
    except:
        # something weird w/ antarctica
        bbox_area_km2 = 0

    try:
        solidity = area_km2 / bbox_area_km2
    except ZeroDivisionError:
        solidity = 0
    feature['properties'].update({
        'area_km2': area_km2,
        'bbox_area_km2': bbox_area_km2,
        'solidity': solidity
    })


def process_countries(geojson):
    features = []
    for idx, feature in enumerate(geojson['features']):
        calculate_properties(feature)
        feature['properties']['index'] = idx
        process_country(feature)


def run(args):
    assert len(args) == 2
    geojson = json.load(file(args[1]))
    assert geojson['type'] == 'FeatureCollection'

    print '\t'.join(fields)

    process_countries(geojson)


if __name__ == '__main__':
    run(sys.argv)
