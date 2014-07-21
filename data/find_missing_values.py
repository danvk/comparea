#!/usr/bin/env python
'''Outputs a spreadsheet calling out missing properties for each feature.'''

import json
import sys

from data import generate_geojson

data = json.load(file('comparea/static/data/comparea.geo.json'))

defaults = generate_geojson.DEFAULT_METADATA
fields = defaults.keys()
fields.sort()
print 'ID\tName\t' + '\t'.join(fields)

for feature in data['features']:
    props = feature['properties']
    vals = [feature['id'], props['name']]
    for field in fields:
        try:
            val = props[field]
            vals.append('x' if val == defaults[field] else '')
        except KeyError:
            vals += '?'
    print '\t'.join(vals).encode('utf-8')
