# -*- coding: utf-8 -*-
import json
import unittest

import extruct
from tests import get_testdata, jsonize_dict


class TestGeneric(unittest.TestCase):

    maxDiff = None

    def test_all(self):
        body = get_testdata('songkick', 'elysianfields.html')
        expected = json.loads(get_testdata('songkick', 'elysianfields.json').decode('UTF-8'))
        data = extruct.extract(body, base_url='http://www.songkick.com/artists/236156-elysian-fields')
        self.assertEqual(jsonize_dict(data), expected)

    def test_microdata_custom_url(self):
        body, expected = self._microdata_custom_url()
        data = extruct.extract(body, base_url='http://some-example.com',
                               syntaxes=['microdata'])
        self.assertEqual(data, expected)

    def test_deprecated_url(self):
        body, expected = self._microdata_custom_url()
        data = extruct.extract(body, url='http://some-example.com',
                               syntaxes=['microdata'])
        self.assertEqual(data, expected)

    def test_extra_kwargs(self):
        body, expected = self._microdata_custom_url()
        with self.assertRaises(TypeError):
            extruct.extract(body, foo='bar')

    def _microdata_custom_url(self):
        body = get_testdata('schema.org', 'product.html')
        expected = {'microdata': json.loads(
            get_testdata('schema.org', 'product_custom_url.json')
            .decode('UTF-8'))}
        return body, expected
