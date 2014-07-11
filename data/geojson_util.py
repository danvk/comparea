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
def _lon_lats_to_shape(lon_lats, p=pa):
    lon, lat = zip(*lon_lats)
    x, y = p(lon, lat)
    cop = {"type": "Polygon", "coordinates": [zip(x, y)]}
    return shape(cop)


def get_area_of_polygon(lon_lats):
    '''lon_lats is an Nx2 list. Returns area in m^2.'''
    return _lon_lats_to_shape(lon_lats).area


def get_area_of_feature(feature):
    geom = feature['geometry']
    if geom['type'] == 'Polygon':
        return get_area_of_polygon(geom['coordinates'][0])
    elif geom['type'] == 'MultiPolygon':
        return sum([get_area_of_polygon(part[0]) for part in geom['coordinates']])


def get_bbox_of_polygon(lon_lats, p):
    return _lon_lats_to_shape(lon_lats, p).bounds


def get_bbox_of_feature(feature, p):
    geom = feature['geometry']
    if geom['type'] == 'Polygon':
        return get_bbox_of_polygon(geom['coordinates'][0], p)
    elif geom['type'] == 'MultiPolygon':
        boxes = [get_bbox_of_polygon(part[0], p) for part in geom['coordinates']]
        col = lambda i: [b[i] for b in boxes]
        return (min(col(0)), min(col(1)), max(col(2)), max(col(3)))


def get_bbox_area_of_feature(feature):
    cx, cy = centroid_of_feature(feature)
    p = Proj(proj='sterea', lat_0=cy, lon_0=cx, k_0=0.9999079, x_0=0, y_0=0)
    x_min, y_min, x_max, y_max = get_bbox_of_feature(feature, p)
    return (x_max - x_min) * (y_max - y_min)


def centroid_of_feature(feature):
    geom = feature['geometry']
    if geom['type'] == 'Polygon':
        pt, _ = _centroid_of_polygon(geom['coordinates'][0])
        return pt.x, pt.y
    elif geom['type'] == 'MultiPolygon':
        sums = [0, 0, 0]
        for part in geom['coordinates']:
            pt, A = _centroid_of_polygon(part[0])
            sums[0] += pt.x * A
            sums[1] += pt.y * A
            sums[2] += A
        return sums[0] / sums[2], sums[1] / sums[2]


def _centroid_of_polygon(lon_lats):
    cop = {"type": "Polygon", "coordinates": [lon_lats]}
    s = shape(cop)
    return s.centroid, s.area
