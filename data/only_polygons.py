#!/usr/bin/env python
'''Removes all non-polygon features from a GeoJSON file.

For now, these must be FeatureCollections of Features.
'''

import sys
import json

OK_GEOMETRIES = ['Polygon', 'MultiPolygon']

def remove_non_polygons(d):
    assert d['type'] == 'FeatureCollection'

    indices_to_delete = []
    for idx, feat in enumerate(d['features']):
        assert feat['type'] == 'Feature'
        if feat['geometry']['type'] == 'GeometryCollection':
            indices = []
            for i, geom in enumerate(feat['geometry']['geometries']):
                if geom['type'] not in OK_GEOMETRIES:
                    indices.append(i)
            for i in reversed(indices):
                del feat['geometry']['geometries'][i]
        elif feat['geometry']['type'] not in OK_GEOMETRIES:
            indices_to_delete.append(idx)

    for idx in reversed(indices_to_delete):
        del d['features'][idx]


if __name__ == '__main__':
    assert len(sys.argv) == 2
    d = json.load(file(sys.argv[1]))
    print json.dumps(d, indent=2)
