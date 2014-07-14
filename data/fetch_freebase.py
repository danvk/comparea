#!/usr/bin/env python
'''Load freebase topic JSON for each feature.

This includes goodies like descriptions, population and area.
'''

import json
import urllib

api_key = open("data/.freebase_api_key").read()
service_url = 'https://www.googleapis.com/freebase/v1/topic'
params = {
    'key': api_key,
    'filter': 'commons'
}

TMP_DIR = '/var/tmp/wiki'

keys = []
gj = json.load(file("comparea/static/data/comparea.geo.json"))
for feature in gj['features']:
    props = feature['properties']
    url = props['wikipedia_url']
    title = url.replace('http://en.wikipedia.org/wiki/', '')
    topic_id = '/wikipedia/en_title/%s' % title
    url = service_url + topic_id + '?' + urllib.urlencode(params)
    print url
    open(TMP_DIR + '/%s.json' % title, 'w').write(urllib.urlopen(url).read())
