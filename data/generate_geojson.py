#!/usr/bin/env python
'''Munge Natural Earth GeoJSON into a format comparea likes.

Usage:
    ogr2ogr -f GeoJSON countries.geo.json ne_50m_admin_0_countries_lakes.shp
    ./generate_geojson.py countries.geo.json > comparea.geo.json
'''

import json
import sys
import os
from data import geojson_util
from data import country_codes


_descs = None
def get_description(code):
    global _descs
    if not _descs:
        p = os.path.join(os.path.dirname(__file__), 'descriptions.json')
        _descs = json.load(file(p))
    try:
        return _descs[code]
    except KeyError:
        return 'A lovely place!'


def process_country(country):
    assert country['type'] == 'Feature'
    props = country['properties']
    out_props = {}
    out = {
        'type': country['type'],
        'geometry': country['geometry'],
        'properties': out_props
    }

    iso3 = props['su_a3']
    out['id'] = iso3
    out_props['name'] = props['name']
    out_props['population'] = props['pop_est']
    out_props['population_year'] = '???'
    out_props['area_km2'] = geojson_util.get_area_of_feature(country) / 1e6
    out_props['description'] = get_description(iso3)
    wiki_url = country_codes.iso3_to_wikipedia_url(iso3)
    if not wiki_url:
        raise ValueError('Unable to get wikipedia link for %s = %s\n' % (iso3, props['name']))
    out_props['wikipedia_url'] = wiki_url

    return out


def process_subunit(country):
    assert country['type'] == 'Feature'
    props = country['properties']
    ids = {
            'FRX': 'France (Metropolitan)',
            'NLD': 'Netherlands',
            'NZ1': 'New Zealand (North Island)',
            'NZS': 'New Zealand (South Island)',
            'PRX': 'Portugal',
            'CHL': 'Chile',
            'NOR': 'Norway',
            'ESX': 'Spain',
            'ZAX': 'South Africa'
    }
    su_a3 = props['su_a3']
    if su_a3 not in ids:
        return None

    out_props = {}
    out = {
        'type': country['type'],
        'geometry': country['geometry'],
        'properties': out_props
    }
    out['id'] = su_a3
    out_props['name'] = ids[su_a3]
    out_props['population'] = props['pop_est']
    out_props['population_year'] = '???'
    out_props['area_km2'] = geojson_util.get_area_of_feature(country) / 1e6
    out_props['description'] = get_description(su_a3)
    out_props['wikipedia_url'] = 'http://google.com'

    return out


def process_province(province):
    assert province['type'] == 'Feature'
    props = province['properties']
    out_props = {}
    out = {
        'type': province['type'],
        'geometry': province['geometry'],
        'properties': out_props
    }

    short_admin = 'USA' if props['iso_a2'] == 'US' else props['admin']
    code = props['code_hasc'].replace('.', '_')
    if short_admin == 'Brazil' and props['hasc_maybe'] and len(code) < 5:
        code = props['hasc_maybe'].split('|')[0].replace('.', '_')
    out['id'] = code
    out_props['name'] = '%s (%s)' % (props['name'], short_admin)
    out_props['population'] = -1
    out_props['population_year'] = '???'
    out_props['area_km2'] = geojson_util.get_area_of_feature(province) / 1e6
    out_props['description'] = 'A nice place'
    wiki_url = props['wikipedia']
    if wiki_url:
        out_props['wikipedia_url'] = wiki_url
    else:
        out_props['wikipedia_url'] = '#'

    return out


def process_continent(continent):
    assert continent['type'] == 'Feature'
    props = continent['properties']
    ids = {
            'Australia': None,  # covered by admin-0,
            'Antarctica': None,  # covered by admin-0
            'Africa': 'AF',
            'South America': 'SA',
            'North America': 'NA',
            'Europe': 'EU',
            'Asia': 'Asia'
    }
    name = props['name'].title()
    if ids[name] == None:
        return None

    out_props = {}
    out = {
        'type': continent['type'],
        'geometry': continent['geometry'],
        'properties': out_props
    }

    out['id'] = ids[name]
    out_props['name'] = name
    out_props['population'] = -1
    out_props['population_year'] = '???'
    out_props['area_km2'] = geojson_util.get_area_of_feature(continent) / 1e6
    out_props['description'] = 'A nice place'
    out_props['wikipedia_url'] = '#'

    return out


def adjust_countries(countries, subunits):
    '''Reconcile related features, e.g. USA and USA (lower 48).'''
    def assert_has_id(feature):
        assert 'id' in feature, 'Missing id from %s' % feature['properties']['name']

    for feat in countries:
        assert_has_id(feat)
    for feat in subunits:
        assert_has_id(feat)

    def find(collection, key):
        matches = [c for c in collection if c['id'] == key]
        assert matches, 'No id %s in collection' % key
        return matches[0]
    def delete(collection, key):
        idx = [i for i, c in enumerate(collection) if c['id'] == key][0]
        del collection[idx]

    find(countries, 'FRA')['properties']['name'] = 'France (Overseas Territories)'

    nld = find(countries, 'NLD')
    nld['properties']['name'] = 'Netherlands (Overseas Territories)'
    nld['id'] = 'NLX'

    find(countries, 'PR1')['properties']['name'] = 'Portugal (Overseas Territories)'
    find(countries, 'NOR')['properties']['name'] = 'Norway (Overseas Territories)'
    find(subunits, 'NOR')['id'] = 'NRX'
    find(countries, 'ESP')['id'] = 'Spain (Overseas Territories)'

    delete(countries, 'CHL')  # replaced by "mainland Chile"
    delete(countries, 'ZAF')  # I don't care about the Prince Edward Islands

    usa48 = geojson_util.subset_feature(find(countries, 'USA'),
            [-126.782227, -66.269531], [24.246965, 49.61071])
    usa48['id'] = 'USA48'
    usa48['properties']['name'] = 'United States (Contiguous 48)'
    countries.append(usa48)

    nz = geojson_util.subset_feature(find(countries, 'NZL'),
            [164, 179], [-49, -32.7])

    delete(countries, 'NZL')
    countries.append(nz)

    return countries + subunits


def assert_no_id_collisions(comparea_features):
    id_to_name = {}
    for feature in comparea_features['features']:
        this_id = feature['id']
        this_name = feature['properties']['name']

        if this_id in id_to_name:
            sys.stderr.write('Duplicate id %s, used by %s and %s\n' % (this_id, id_to_name[this_id], this_name))
            raise ValueError('Duplicate id %s, used by %s and %s' % (this_id, id_to_name[this_id], this_name))
        id_to_name[this_id] = this_name


def process_features(geojson, fn):
    features = []
    for feature in geojson['features']:
        f = fn(feature)
        if f:
            features.append(f)

    return features


def load_geojson(filename, process_fn):
    p = os.path.join(os.path.dirname(__file__), filename)
    geojson = json.load(file(p))
    assert geojson['type'] == 'FeatureCollection'
    features = process_features(geojson, process_fn)
    # geojson_util.check_feature_collection(features)
    return features


def run(args):
    countries = load_geojson('countries.json', process_country)
    subunits = load_geojson('subunits.json', process_subunit)
    admin0 = adjust_countries(countries, subunits)

    collections = [
        admin0,
        load_geojson('provinces.json', process_province),
        load_geojson('continents.json', process_continent)
            ]

    comparea_features = {
            'type': 'FeatureCollection',
            'features': collections[0] }

    for collection in collections[1:]:
        comparea_features['features'] += collection

    assert_no_id_collisions(comparea_features)

    print json.dumps(comparea_features)


if __name__ == '__main__':
    run(sys.argv)
