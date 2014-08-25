#!/usr/bin/python
'''Generates sitemap files for Googlebot.

There's a 50MB / 50,000 URL limit on each sitemap file, so this will actually
generate many sitemap files in a single directory.

Usage:
    ./data/generate_sitemap.py comparea/static/data/comparea.geo.json comparea/static/sitemaps
'''

from datetime import datetime
import itertools
import json
import os
import sys

def get_ids(geojson):
    return [x['id'] for x in geojson['features']]


def all_pairs(items):
    return itertools.combinations(items, 2)


def sitemap_xml_for_url(id1, id2):
    return '<url><loc>http://www.comparea.org/%s+%s</loc></url>' % (id1, id2)


def sitemap_xml(pairs):
    url_xmls = [sitemap_xml_for_url(x[0], x[1]) for x in pairs if x]
    return '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"> 
%s
</urlset>
''' % '\n'.join(url_xmls)


# From https://docs.python.org/2/library/itertools.html
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)


def sitemap_xml_files(geojson):
    '''Yields individual XML files.'''
    pairs = all_pairs(get_ids(geojson))

    for pair_seq in grouper(pairs, 50000):
        yield sitemap_xml(pair_seq)


def generate_index_file(num_sitemaps):
    def entry(index):
        return '''
   <sitemap>
      <loc>http://www.comparea.org/static/sitemaps/%d.xml</loc>
      <lastmod>%s</lastmod>
   </sitemap>''' % (index, datetime.now().replace(microsecond=0).isoformat())
    return '''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">%s
</sitemapindex>
''' % ''.join([entry(x) for x in range(0, num_sitemaps)])


if __name__ == '__main__':
    assert len(sys.argv) == 3
    _, geojson_path, output_path = sys.argv
    assert os.path.isdir(output_path)

    geojson = json.load(open(geojson_path))
    count = 0
    for idx, xml in enumerate(sitemap_xml_files(geojson)):
        path = os.path.join(output_path, '%s.xml' % idx)
        open(path, 'w').write(xml)
        sys.stderr.write('Wrote %d bytes to %s\n' % (len(xml), path))
        count = idx + 1

    index_path = os.path.join(output_path, 'index.xml')
    xml = generate_index_file(count)
    open(index_path, 'w').write(xml)
    sys.stderr.write('Wrote %d bytes to %s\n' % (len(xml), index_path))
