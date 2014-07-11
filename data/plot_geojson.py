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
    map.plot(lon, lat, color='r', latlon=True)


def plot_feature(map, feature):
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
    # draw great circle route

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
