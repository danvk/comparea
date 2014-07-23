#!/usr/bin/env python
'''Summarize Natural Earth GeoJSON.
'''

import json
import sys
import geojson_util

fields = ['index', 'id', 'name', 'area_km2', 'area_calculated']


def fmt(x):
    if type(x) == int or type(x) == float:
        return str(x)
    else:
        return x


def process_feature(feature):
    props = feature['properties']
    print ('\t'.join([fmt(props[f]) for f in fields])).encode('utf-8')


def calculate_properties(feature):
    area_km2 = geojson_util.get_area_of_feature(feature) / 1e6

    feature['properties'].update({
        'area_calculated': area_km2,
        'id': feature['id']
    })


def process_features(geojson):
    features = []
    for idx, feature in enumerate(geojson['features']):
        calculate_properties(feature)
        feature['properties']['index'] = idx
        process_feature(feature)


def run(args):
    assert len(args) == 2
    geojson = json.load(file(args[1]))
    assert geojson['type'] == 'FeatureCollection'

    print '\t'.join(fields)

    process_features(geojson)


if __name__ == '__main__':
    run(sys.argv)
