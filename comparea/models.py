import json
import os

p = os.path.join(os.path.dirname(__file__), 'static/data/countries.geo.json')
data = json.load(file(p))

def feature_for_iso3(iso3):
    for feature in data['features']:
        if feature['id'] == iso3:
            return feature
    return None

def all_countries():
    '''Returns (country name, id) tuples.'''
    return sorted([(f['properties']['name'], f['id']) for f in data['features']])
