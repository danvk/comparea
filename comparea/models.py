import json
import os

def _load_data():
    p = os.path.join(os.path.dirname(__file__), 'static/data/comparea.geo.json')
    return json.load(open(p))

def feature_for_code(code):
    for feature in DATA['features']:
        if feature['id'] == code:
            return feature
    return None

def all_countries():
    '''Returns (name, id) tuples.'''
    return sorted([(f['properties']['name'], f['id']) for f in DATA['features']])

def page_title(shape1, shape2):
    '''Returns a title for the Comparea page.'''
    return '%s vs. %s: Comparea Area Comparison' % (
            shape1['properties']['name'], shape2['properties']['name'])

def reload_data():
    global DATA
    DATA = _load_data()

reload_data()
