#!/usr/bin/env python
'''This script fetches freebase data for OSM features.

Input is a CSV file looking like:

    osm_type,osm_id,wikipedia_title,name

This doesn't output anything, it just populates the local freebase cache.
'''

import csv
import sys
import time
import urllib2
import os

from data import freebase


if __name__ == '__main__':
    csv = csv.reader(open(sys.argv[1], 'rb'))
    fb = freebase.Freebase()

    for idx, row in enumerate(csv):
        osm_type, osm_id, wiki_title, name = row
        if wiki_title.startswith("en:"):
            wiki_title = wiki_title[3:]
        if '://' in wiki_title:
            continue

        try:
            fb.get_topic_json(wiki_title)
        except urllib2.HTTPError:
            sys.stderr.write("Failed to fetch fb data for %s\n" % wiki_title)
            pass
        except:
            sys.stderr.write("Other error on %s\n" % wiki_title)
            pass
        if idx % 100 == 0:
            sys.stderr.write('%d...\n' % idx)
