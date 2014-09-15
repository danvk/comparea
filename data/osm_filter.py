#!/usr/bin/env python
'''Produces a small list of OSM (type, id) pairs for inclusion in Comparea.

Inclusion criteria:
    - feature has an associated English Wikipedia article
    - feature contains Polygons or MultiPolygons (not just lines or points)
    - feature is either:
      * a park with wiki articles in >= 10 languages
      * an non-county administrative region with population >= 100,000
      * in a small whitelist of counties

Output is
    type<tab>id<tab>wikipedia article<tab>name<tab>reasons for inclusion
'''

import csv
import json
import os
import sys
from data import osm
from data import fetch_metadata
from data import freebase

COUNTY_WHITELIST = {
        'Los Angeles County': 'Los Angeles County',
        'Cook County': 'Cook County, Illinois',
        'Harris County': 'Harris County, Texas',
        'Orange County': 'Orange County, California',
        'New York County': 'Manhattan',
        'Kings County': 'Brooklyn',
        'Queens County': 'Queens',
        'Bronx County': 'The Bronx',
        'Richmond County': 'Staten Island'
        }

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


def is_english_wikititle(wiki_title):
    if wiki_title.startswith("en:"):
        return True
    if '://' in wiki_title:
        return False
    if len(wiki_title) > 3 and wiki_title[2] == ':':
        return False
    return True


def get_feature_props(geojson, osm_type, osm_id):
    '''Returns the 'properties' field of the main feature.'''
    props = None
    try:
        correct_id = '%s/%s' % (osm_type, osm_id)
        for f in geojson['features']:
            if f['id'] == correct_id:
                props = f['properties']
                break
    except IndexError:
        return None
    return props


def main(args):
    assert len(args) == 2
    csv_reader = csv.reader(open(sys.argv[1], 'rb'))
    fb = freebase.Freebase()
    osm_fetcher = osm.OSM()

    for idx, row in enumerate(csv_reader):
        osm_type, osm_id, wiki_title, name = row
        if not is_english_wikititle(wiki_title):
            continue
        if wiki_title.startswith("en:"):
            wiki_title = wiki_title[3:]

        path = os.path.join(osm_fetcher.cache_dir,
                '%s%s.xml.json' % (osm_type, osm_id))
        try:
            d = json.load(file(path))
        except (ValueError, IOError):
            continue

        props = get_feature_props(d, osm_type, osm_id)
        if not props:
            continue

        if not has_polygon(d):
            continue
        freebase_data = fb._get_from_cache(wiki_title)
        if not freebase_data:
            continue

        try:
            total_languages = len(freebase_data['property']['/common/topic/topic_equivalent_webpage']['values'])
        except KeyError:
            total_languages = 0

        pass_condition = None
        if props.get('leisure') == 'park':
            if total_languages >= 10:
                pass_condition = ['park', str(total_languages)]
        admin_level = props.get('admin_level')
        if admin_level:
            admin_level = int(admin_level)
            if admin_level <= 4:
                continue  # no states, countries -- other sources cover these.
            # Counties are generally not that interesting, with a few
            # exceptions like NYC boroughs and Los Angeles.
            if 'County' in name:
                if name not in COUNTY_WHITELIST:
                    continue

            d = fetch_metadata.extract_freebase_metadata('', wiki_title, freebase_data)
            if d.get('population', 0) >= 100000:
                pass_condition = ['admin_pop', str(admin_level), str(d.get('population'))]

        if pass_condition:
            print '\t'.join(row + pass_condition)



if __name__ == '__main__':
    main(sys.argv)
