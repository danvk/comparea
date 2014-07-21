#!/usr/bin/env python

'''Construct a mapping from Comparea ID --> freebase properties.

These include:
    - Description
    - Population
    - Area
'''

import json
import re
import sys

from data import cia
from data import freebase
from data import spreadsheet


def trim_description(desc, max_chars=200):
    '''Cut off the description on sentence boundaries.'''
    if len(desc) < max_chars:
        return desc

    result = ''
    sentences = re.split(r'\.[ \n]', desc)

    while len(result) < max_chars and sentences:
        next_sentence = sentences[0]
        if len(result) + len(next_sentence) + 2 <= max_chars:
            if len(result):
                result += ' '
            del sentences[0]
            result += next_sentence
            if sentences:
                result += '.'
        else:
            break
    return result


# Freebase helper accessors
def get_value_obj(v, key):
    return v['property'][key]['values'][0]
def get_value(v, key):
    return get_value_obj(v, key)['value']


def extract_population(pop_topic, metadata):
    '''Fills in metadata.populaton{,_year,_source,_source_url}.'''
    if pop_topic['valuetype'] != 'compound': return

    def get_year(v):
        return get_value(v, '/measurement_unit/dated_integer/year')
    def has_source(v):
        try:
            get_value_obj(v, '/measurement_unit/dated_integer/source')
            return True
        except KeyError:
            return False

    vals = filter(has_source, pop_topic['values'])
    if not vals:
        return
    vals.sort(key=get_year)
    latest_value = vals[-1]

    metadata['population'] = get_value(latest_value, '/measurement_unit/dated_integer/number')
    metadata['population_date'] = get_value(latest_value, '/measurement_unit/dated_integer/year')

    source = get_value_obj(latest_value, '/measurement_unit/dated_integer/source')
    metadata['population_source'] = source['citation']['provider']
    metadata['population_source_url'] = source['citation']['uri']


def extract_freebase_metadata(title, d):
    '''d is the freebase Topic JSON response'''
    metadata = {}
    metadata['freebase_mid'] = d['id']

    # Description
    try:
        desc_topic = d['property']['/common/topic/description']
        en_values = [v['value'] for v in desc_topic['values'] if v['lang'] == 'en']
        en_values.sort(key=lambda x: -len(x))
        en_value = en_values[0]
        metadata['description'] = trim_description(en_value, max_chars=300)
    except KeyError:
        sys.stderr.write('Missing description for %s\n' % title)

    # Population
    try:
        pop = d['property']['/location/statistical_region/population']
        extract_population(pop, metadata)
    except KeyError:
        pass

    # Area
    try:
        metadata['area_km2'] = get_value(d, '/location/location/area')
    except KeyError:
        pass

    return metadata


def run():
    freebase_api = freebase.Freebase()

    output = {}
    gj = json.load(file("comparea/static/data/comparea.geo.json"))
    wiki_url_prefix = 'http://en.wikipedia.org/wiki/'

    for feature in gj['features']:
        key = feature['id']
        props = feature['properties']
        url = props['wikipedia_url']
        title = freebase.wiki_url_to_title(url)
        if not title:
            sys.stderr.write('ERROR %s has invalid wiki URL: %s\n' % (title, url))
            continue

        try:
            d = freebase_api.get_topic_json(title)
        except IOError:
            sys.stderr.write('ERROR unable to fetch %s\n' % title)
            continue

        if 'error' in d:
            sys.stderr.write('ERROR unable to fetch %s\n' % title)
            continue
        
        md = extract_freebase_metadata(title, d)
        try:
            md.update(cia.get_country_data(key))
        except KeyError:
            pass  # no CIA data
        try:
            md.update(spreadsheet.get_feature_data(key))
        except KeyError:
            pass  # no manual data
        output[key] = md

    print json.dumps(output, indent=2, sort_keys=True)


if __name__ == '__main__':
    run()
