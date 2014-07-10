#!/usr/bin/env python

import base64
import json
import os
import requests
import re
import sys
import time
from bs4 import BeautifulSoup

from data import country_codes
TMP_DIR = '/var/tmp/wiki'

def get_urls():
    country_codes.iso3_to_wikipedia_url('USA')
    return country_codes.iso3_to_url.items()

def cache_path(url):
    x = url.replace('http://en.wikipedia.org/wiki/', '')
    x = re.sub(r'[^a-zA-Z0-9_]', '_', x) + '.html'
    return os.path.join(TMP_DIR, x)

def fetch_url(url):
    cache_file = cache_path(url)
    if os.path.exists(cache_file):
        return open(cache_file).read()

    time.sleep(1.0)  # 1 second
    r = requests.get(url)
    if r.ok:
        open(cache_file, 'wb').write(r.content)
        return r.content
    else:
        raise ValueError('Unable to fetch %s' % url)


def extract_paragraph(html, max_length=500):
    '''Extract the first paragraph of content from a Wikipedia article.'''
    soup = BeautifulSoup(html)
    ps = soup.find(id="mw-content-text").find_all('p')

    # This is a bit of a hack: the first body paragraph always has bold text.
    first_p = None
    for p in ps:
        if p.find('b'):
            first_p = p
            break
    if not first_p:
        raise ValueError('Unable to find first paragraph')

    p = first_p
    for x in p.select('.nowrap'): x.clear()  # these are never interesting
    txt = p.get_text()

    txt = re.sub(r' \([^)]+\)', '', txt, count=1)  # rm first parenthetical bit.
    txt = re.sub(r'\[\d+\]', '', txt)  # remove references
    txt = re.sub(r' , ', ', ', txt)  # cleanup

    sentences = txt.split('. ')
    result = ''
    while len(result) < max_length and sentences:
        next_sentence = sentences[0]
        if len(result) + len(next_sentence) + 2 <= max_length:
            if len(result):
                result += ' '
            del sentences[0]
            result += next_sentence
            if sentences:
                result += '.'
        else:
            break
    return result


if __name__ == '__main__':
    out = {}
    for code, url in get_urls():
        sys.stderr.write('%s: %s\n' % (code, url))
        html = fetch_url(url)
        desc = extract_paragraph(html)
        out[code] = desc

    print json.dumps(out, indent=2, sort_keys=True)
