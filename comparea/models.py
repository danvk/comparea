import json
import os

# TODO(danvk): use a database
p = os.path.join(os.path.dirname(__file__), 'static/data/comparea.geo.json')
data = json.load(file(p))

def feature_for_code(code):
    for feature in data['features']:
        if feature['id'] == code:
            return feature
    return None

def all_countries():
    '''Returns (name, id) tuples.'''
    return sorted([(f['properties']['name'], f['id']) for f in data['features']])
