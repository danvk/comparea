#!/usr/bin/env python
'''Removes all non-polygon features from a GeoJSON file.

For now, these must be FeatureCollections of Features.
'''

import sys
import json

def remove_non_polygons(d):
    assert d['type'] == 'FeatureCollection'

    indices_to_delete = []
    for idx, feat in enumerate(d['features']):
        assert feat['type'] == 'Feature'
        if feat['geometry']['type'] not in ['Polygon', 'MultiPolygon']:
            indices_to_delete.append(idx)

    for idx in reversed(indices_to_delete):
        del d['features'][idx]


if __name__ == '__main__':
    assert len(sys.argv) == 2
    d = json.load(file(sys.argv[1]))
    print json.dumps(d, indent=2)
