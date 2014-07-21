# -*- coding: utf-8 -*-

import json
import unittest

from data import freebase

class FreebaseTest(unittest.TestCase):

    def setUp(self):
        self.freebase = freebase.Freebase(api_key=1234, use_cache=False)

    def tearDown(self):
        pass

    def test_wiki_url_to_title_unicode(self):
        x = "http://en.wikipedia.org/wiki/Cura%C3%A7ao"
        url = x.encode('utf-8')
        title = freebase.wiki_url_to_title(url)
        self.assertEquals(u'Curaçao', title)
        self.assertTrue(self.freebase._construct_url(title).find(
            '/wikipedia/en_title/Cura$00E7ao') != -1)

    def test_wiki_url_to_title_spaces(self):
        url = "http://en.wikipedia.org/wiki/Foo_Bar_Baz"
        title = freebase.wiki_url_to_title(url)
        self.assertEquals(u'Foo Bar Baz', title)
        self.assertTrue(self.freebase._construct_url(title).find(
            '/wikipedia/en_title/Foo_Bar_Baz?') != -1)

    def test_wiki_url_to_title_monkey_patch(self):
        url = "http://en.wikipedia.org/wiki/Myanmar"
        title = freebase.wiki_url_to_title(url)
        self.assertEquals(u'Myanmar', title)
        url = self.freebase._construct_url(title)
        self.assertTrue(url.find('/wikipedia/en_title/Burma?') != -1, url)

        url = "http://en.wikipedia.org/wiki/Vatican_City_State"
        title = freebase.wiki_url_to_title(url)
        self.assertEquals(u'Vatican City State', title)
        url = self.freebase._construct_url(title)
        self.assertTrue(url.find('/wikipedia/en_title/Vatican_City?') != -1, url)

    def test_from_json(self):
        gj = json.load(file("comparea/static/data/comparea.geo.json"))
        curacao = None
        for feature in gj['features']:
            if feature['id'] == 'CUW':
                curacao = feature
                break

        assert curacao
        props = curacao['properties']
        url = props['wikipedia_url']
        title = freebase.wiki_url_to_title(url)
        self.assertEquals(u'Curaçao', title)
        self.assertTrue(self.freebase._construct_url(title).find(
            '/wikipedia/en_title/Cura$00E7ao') != -1)

if __name__ == '__main__':
    unittest.main()
