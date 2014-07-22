#!/usr/bin/env python
'''This kills unneeded fields in the Freebase topic cache (to parse faster).'''
import glob
import json
from data import freebase

OK_FIELDS = [
    '/location/statistical_region/population',
    '/location/location/area',
    '/common/topic/description'
]

for p in glob.glob('/var/tmp/freebase/*.json'):
    data = json.load(file(p))
    if 'property' not in data:
        continue  # maybe an error response

    props = data['property']
    ks = props.keys()[:]
    for k in ks:
        if k not in OK_FIELDS:
            del props[k]

    json.dump(data, file(p, 'w'), indent=1, sort_keys=True)
