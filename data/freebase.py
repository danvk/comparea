#!/usr/bin/env python
'''Load freebase topic JSON for each feature.

This includes goodies like descriptions, population and area.
'''

import os
import json
import sys
import urllib

from data import mqlkey

PREDICATE_PREFIXES = ['/location/statistical_region', '/common/topic']

class Freebase(object):
    '''Freebase Topic API wrapper. Maps wikipedia title --> topic JSON.'''
    service_url = 'https://www.googleapis.com/freebase/v1/topic'
    cache_dir = '/var/tmp/freebase'

    def __init__(self, api_key=None, use_cache=True):
        if not api_key:
            api_key = open(os.path.join(os.path.dirname(__file__), '.freebase_api_key')).read()
        self._key = api_key
        self._use_cache = use_cache

    def _cache_file(self, title):
        return os.path.join(self.cache_dir, '%s.json' % title)

    def _get_from_cache(self, title):
        if not self._use_cache: return None
        p = self._cache_file(title)
        if os.path.exists(p):
            try:
                d = json.load(file(p))
            except ValueError:
                sys.stderr.write('Unable to decode json for %s, %s\n' % (title, p))
                raise

            if 'error' in d:
                return None
            sys.stderr.write('Loaded %s from cache.\n' % title)
            return d
        else:
            return None

    def get_topic_json(self, title):
        '''title is a Wikipedia title for the topic.'''
        d = self._get_from_cache(title)
        if d: return d

        params = [
            ('key', self._key),
            ('limit', 1000)  # get population at lots of dates!
        ] + map(lambda x: ('filter', x), PREDICATE_PREFIXES)
        title_key = mqlkey.quotekey(title)
        topic_id = '/wikipedia/en_title/%s' % title_key
        url = self.service_url + topic_id + '?' + urllib.urlencode(params)
        sys.stderr.write('Fetching %s\n' % url)
        data = urllib.urlopen(url).read()
        open(self._cache_file(title), 'w').write(data)
        return json.loads(data)


if __name__ == '__main__':
    freebase = Freebase()

    wiki_url_prefix = 'http://en.wikipedia.org/wiki/'
    gj = json.load(file("comparea/static/data/comparea.geo.json"))
    for feature in gj['features']:
        props = feature['properties']
        url = props['wikipedia_url']
        if wiki_url_prefix not in url:
            sys.stderr.write('ERROR %s has invalid wiki URL: %s\n' % (title, url))
            continue

        title = url.replace(wiki_url_prefix, '')
        try:
            d = freebase.get_topic_json(title)
        except IOError:
            sys.stderr.write('ERROR unable to fetch %s\n' % title)
