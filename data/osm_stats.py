#!/usr/bin/env python
'''Collect statistics about OSM features.'''

from collections import defaultdict
import glob
import json
import os
from data import geojson_util
from data import osm
from bs4 import BeautifulSoup

osm_fetcher = osm.OSM()


def has_polygon(d):
    polys, total = polygon_stats(d)
    return polys > 0

def polygon_stats(d):
    if d['type'] == 'Feature':
        if d['geometry']['type'] in ['Polygon', 'MultiPolygon']:
            return 1, 1
        else:
            return 0, 1
    elif d['type'] == 'FeatureCollection':
        a, b = 0, 0
        for feat in d['features']:
            c, d = polygon_stats(feat)
            a += c
            b += d
        return a, b
    raise ValueError('Unknown feature type %s' % d['type'])


without_polygons = 0
total = 0
leisures = defaultdict(int)
admins = defaultdict(int)

for path in glob.glob(os.path.join(osm_fetcher.cache_dir, '*.json')):
    try:
        d = json.load(file(path))
    except ValueError:
        continue

    if len(d['features']) == 0:
        continue

    props = d['features'][0]['properties']
    
    if not has_polygon(d):
        without_polygons += 1
    if props.get('admin_level'):
        admins[props.get('admin_level')] += 1
    if props.get('leisure'):
        leisures[props.get('leisure')] += 1
    total += 1

print 'Features with no polygons: %d / %d' % (without_polygons, total)
print 'Admin: %s' % admins
print 'Leisures: %s' % leisures
