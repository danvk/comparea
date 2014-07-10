#!/usr/bin/env python
'''Summarize Natural Earth GeoJSON.
'''

import json
import sys

fields = ['su_a3', 'name', 'name_long', 'pop_est', 'pop_year', 'continent', 'region_un', 'subregion']


def fmt(x):
    if type(x) == int or type(x) == float:
        return str(x)
    else:
        return x


def process_country(country):
    assert country['type'] == 'Feature'
    props = country['properties']
    print ('\t'.join([fmt(props[f]) for f in fields])).encode('utf-8')


def process_countries(geojson):
    features = []
    for feature in geojson['features']:
        process_country(feature)


def run(args):
    assert len(args) == 2
    geojson = json.load(file(args[1]))
    assert geojson['type'] == 'FeatureCollection'

    print '\t'.join(fields)

    process_countries(geojson)


if __name__ == '__main__':
    run(sys.argv)
