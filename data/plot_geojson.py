'''This module is intended to be used from IPython Notebooks.

Usage:

    plot_geojson.show_feature(geojson['features'][0])
'''

import json
from pyproj import Proj
from shapely.geometry import shape
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from data import geojson_util


def _plot_polygon(map, lon_lats):
    lon, lat = zip(*lon_lats)
    xx, yy = map(lon, lat)
    plt.fill(xx, yy, color='r')
    plt.plot(xx, yy, color='b', linewidth=10)


def plot_feature(map, feature):
    if feature['type'] == 'FeatureCollection':
        for feat in feature['features']:
            plot_feature(map, feat)
    elif feature['type'] == 'Feature':
        geom = feature['geometry']
        if geom['type'] == 'Polygon':
            _plot_polygon(map, geom['coordinates'][0])
        elif geom['type'] == 'MultiPolygon':
            for part in geom['coordinates']:
                _plot_polygon(map, part[0])


def show_feature(feature):
    fig, ax = plt.subplots(figsize=(12,12))
    map = Basemap(projection='merc', llcrnrlat=-80, urcrnrlat=80,
                llcrnrlon=-180, urcrnrlon=180, resolution='l')

    land_color = 'lightgray'
    water_color = 'lightblue'

    map.fillcontinents(color=land_color, lake_color=water_color)
    map.drawcoastlines()
    map.drawparallels(np.arange(-90.,120.,30.))
    map.drawmeridians(np.arange(0.,420.,60.))
    map.drawmapboundary(fill_color=water_color)
    try:
        ax.set_title(feature['properties']['name'])
    except KeyError:
        pass

    plot_feature(map, feature)

    map.ax = ax

    plt.show()
    return map


# TODO: choose resolution based on geographic extent
def show_feature_centered(feature, resolution='l'):
    fig, ax = plt.subplots(figsize=(12,12))
    cx, cy = geojson_util.centroid_of_feature(feature)

    # Calculate a good bounding box and pad it.
    minlat, minlon, maxlat, maxlon = geojson_util.bbox_of_feature(feature)
    latext = maxlat - minlat
    lonext = maxlon - minlon

    map = Basemap(projection='aea',
            llcrnrlon = minlon - 0.5*lonext,
            llcrnrlat = minlat - 0.5*latext,
            urcrnrlon = maxlon + 0.5*lonext,
            urcrnrlat = maxlat + 0.5*latext,
            resolution=resolution,
            lat_1=40.,lat_2=60,lon_0=cx,lat_0=cy)

    land_color = 'lightgray'
    water_color = 'lightblue'

    map.fillcontinents(color=land_color, lake_color=water_color)
    map.drawcoastlines()
    map.drawparallels(np.arange(-90.,120.,30.))
    map.drawmeridians(np.arange(0.,420.,60.))
    map.drawmapboundary(fill_color=water_color)
    try:
        ax.set_title(feature['properties']['name'])
    except KeyError:
        pass

    plot_feature(map, feature)

    map.ax = ax

    plt.show()
    return map


def show_shape(shape, color='r'):
    '''Displays a shapely.geometry.Shape object.'''
    pts = shape.exterior.coords  # TODO(danvk): remove .interiors
    
    xx, yy = zip(*pts)
    plt.fill(xx, yy, color)
    plt.show()
