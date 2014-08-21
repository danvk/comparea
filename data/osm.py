#!/usr/bin/env python
'''Library for fetching shape data from OSM.

When run from the command line, it will read in a CSV file of:

    osm_type,osm_id,wikipedia_title,name

And fetch all of them into its local cache.
'''

import csv
import sys
import time
import urllib2
import os

class OSM(object):
    service_url = u'http://www.openstreetmap.org/api/0.6'
    cache_dir = '/var/tmp/osm'
    max_fetch_rate = 2.0  # 2.0 seconds between fetches

    def __init__(self, use_cache=True):
        self._use_cache = use_cache
        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)
        self._last_fetch_time = 0

    def _cache_file(self, osm_type, osm_id):
        return os.path.join(self.cache_dir, '%s%s.xml' % (osm_type, osm_id))

    def _get_from_cache(self, osm_type, osm_id):
        if not self._use_cache: return None
        p = self._cache_file(osm_type, osm_id)
        if os.path.exists(p):
            d = file(p).read()
            #sys.stderr.write('Loaded %s/%s from cache.\n' % (osm_type, osm_id))
            return d
        else:
            return None

    def _construct_url(self, osm_type, osm_id):
        url = '%s/%s/%s/full' % (self.service_url, osm_type, osm_id)
        return url

    def get_osm_data(self, osm_type, osm_id):
        '''osm_type is in ['node', 'way', 'relation'] and osm_id is a number.

        Returns XML'''
        d = self._get_from_cache(osm_type, osm_id)
        if d: return d

        url = self._construct_url(osm_type, osm_id)
        now = time.time()
        if now - self._last_fetch_time < self.max_fetch_rate:
            time.sleep(now - self._last_fetch_time)

        self._last_fetch_time = time.time()
        # 10 second timeout
        sys.stderr.write('%s Fetching %s\n' % (time.ctime(), url))
        data = urllib2.urlopen(url, None, 10).read()
        open(self._cache_file(osm_type, osm_id), 'w').write(data)
        return data


if __name__ == '__main__':
    csv = csv.reader(open(sys.argv[1], 'rb'))
    osm = OSM()

    for row in csv:
        osm_type, osm_id, wiki_title, name = row[:4]
        try:
            osm.get_osm_data(osm_type, osm_id)
        except IOError:
            sys.stderr.write('IO Error!\n')
            pass

