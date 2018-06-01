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
        body, expected = self._microdata_custom_url('product_custom_url.json')
        data = extruct.extract(body, base_url='http://some-example.com',
                               syntaxes=['microdata'])
        self.assertEqual(data, expected)

    def test_microdata_with_returning_node(self):
        body, expected = self._microdata_custom_url('product_custom_url_and_node_id.json')
        data = extruct.extract(body, base_url='http://some-example.com',
                               syntaxes=['microdata'], return_html_node=True)
        self._replace_node_ref_with_node_id(data)
        self.assertEqual(data, expected)

    def test_deprecated_url(self):
        body, expected = self._microdata_custom_url('product_custom_url.json')
        data = extruct.extract(body, url='http://some-example.com',
                               syntaxes=['microdata'])
        self.assertEqual(data, expected)

    def test_extra_kwargs(self):
        body, expected = self._microdata_custom_url('product_custom_url.json')
        with self.assertRaises(TypeError):
            extruct.extract(body, foo='bar')

    def _microdata_custom_url(self, test_file):
        body = get_testdata('schema.org', 'product.html')
        expected = {'microdata': json.loads(
            get_testdata('schema.org', test_file)
            .decode('UTF-8'))}
        return body, expected

    def _replace_node_ref_with_node_id(self, item):
        if isinstance(item, list):
            for i in item:
                self._replace_node_ref_with_node_id(i)
        if isinstance(item, dict):
            for key in list(item):
                val = item[key]
                if key == "htmlNode":
                    item["_nodeId_"] = val.get("id")
                    del item[key]
                else:
                    self._replace_node_ref_with_node_id(val)





