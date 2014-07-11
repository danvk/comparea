import json
from pyproj import Proj
from shapely.geometry import shape

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
    for prop in ['type', 'properties', 'id']:
        if prop not in feature:
            raise ValueError('Feature is missing "%s" field.' % prop)

    if feature['type'] != 'Feature':
        raise ValueError('Expected type=Feature, got type=%s' % feature['type'])

    for prop in ['name', 'population', 'population_year', 'area_km2', 'description']:
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


pa = Proj("+proj=aea +lat_1=37.0 +lat_2=41.0 +lat_0=39.0 +lon_0=-106.55")
def get_area_of_polygon(lat_lons):
    '''lat_lons is an Nx2 list. Returns area in m^2.'''
    global pa
    lon, lat = zip(*lat_lons)
    x, y = pa(lon, lat)
    cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
    return shape(cop).area


def get_area_of_feature(feature):
    geom = feature['geometry']
    if geom['type'] == 'Polygon':
        return get_area_of_polygon(geom['coordinates'][0])
    elif geom['type'] == 'MultiPolygon':
        return sum([get_area_of_polygon(part[0]) for part in geom['coordinates']])
    # 9,300,085.21879031
