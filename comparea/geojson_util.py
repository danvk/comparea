import json

'''
GeoJSON looks like:

    { type: "FeatureCollection",
      features: [
        type: "Feature",
        properties: { "a": "b", "c": 1.0 },
        geometry: { ... }
      ]}
'''

def check_feature(feature):
    '''Checks that a GeoJSON feature has the required attributes.

    Throws a descriptive error if anything is wrong.
    '''
    if 'type' not in feature:
        raise ValueError('feature needs a "type" field.')

    if feature['type'] != 'Feature':
        raise ValueError('Expected type=Feature, got type=%s' % feature['type'])

    if 'properties' not in feature:
        raise ValueError('Feature is missing "properties" field.')

    for prop in ['id', 'name', 'pop', 'pop_year', 'area_km2', 'description']:
        if prop not in feature['properties']:
            raise ValueError('Feature is missing %s property' % prop)


def check_feature_collection(collection):
    if 'type' not in collection:
        raise ValueError('feature collection needs a "type" field.')

    if collection['type'] != 'FeatureCollection':
        raise ValueError('Expected type=FeatureCollection, got type=%s' % collection['type'])

    if 'features' not in collection or len(collection['features']) == 0:
        raise ValueError('FeatureCollection is missing features')

    for i, feature in enumerate(collection['features']):
        try:
            check_feature(feature)
        except ValueError as e:
            raise ValueError('(feature %d) %s' % (i, e))
