import json
import os
import unittest
import math

from data import geojson_util


def _path(filename):
    return os.path.join(os.path.dirname(__file__), filename)


class GeoJsonUtilTest(unittest.TestCase):

    def setUp(self):
        self.kgz = json.load(file(_path('kgz.json')))

    def tearDown(self):
        pass

    def test_get_area_of_polygon(self):
        coords = self.kgz['geometry']['coordinates'][0]
        self.assertEquals(349, len(coords))
        area = geojson_util.get_area_of_polygon(coords)
        area_km2 = area / 1e6
        self.assertEquals(199486, round(area_km2))

    def test_get_area_of_feature(self):
        area = geojson_util.get_area_of_feature(self.kgz)
        area_km2 = area / 1e6
        self.assertEquals(199486, round(area_km2))


if __name__ == '__main__':
    unittest.main()
