import json
import os

def _load_data():
    p = os.path.join(os.path.dirname(__file__), 'static/data/comparea.geo.json')
    return json.load(file(p))

def feature_for_code(code):
    for feature in DATA['features']:
        if feature['id'] == code:
            return feature
    return None

def all_countries():
    '''Returns (name, id) tuples.'''
    return sorted([(f['properties']['name'], f['id']) for f in DATA['features']])

def reload_data():
    global DATA
    DATA = _load_data()

reload_data()
