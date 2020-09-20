# -*- coding: utf-8 -*-
import json
import unittest

import pytest

import extruct
from extruct import SYNTAXES
from tests import get_testdata, jsonize_dict, replace_node_ref_with_node_id


class TestGeneric(unittest.TestCase):

    maxDiff = None

    def test_all(self):
        body = get_testdata('songkick', 'elysianfields.html')
        expected = json.loads(get_testdata('songkick', 'elysianfields.json').decode('UTF-8'))
        data = extruct.extract(body, base_url='http://www.songkick.com/artists/236156-elysian-fields')
               
        self.assertEqual(jsonize_dict(data), expected)

    def test_rdfa_is_preserving_order(self):
        # See https://github.com/scrapinghub/extruct/issues/116
        body = get_testdata('songkick', 'elysianfields_1.html')
        expected = json.loads(get_testdata('songkick', 'elysianfields_1.json').decode('UTF-8'))
        data = extruct.extract(body,
                               base_url='http://www.songkick.com/artists/236156-elysian-fields')
        self.assertEqual(jsonize_dict(data)['rdfa'], expected['rdfa'])

    def test_microdata_custom_url(self):
        body, expected = self._microdata_custom_url('product_custom_url.json')
        data = extruct.extract(body, base_url='http://some-example.com',
                               syntaxes=['microdata'])
        self.assertEqual(data, expected)

    def test_microdata_with_returning_node(self):
        body, expected = self._microdata_custom_url('product_custom_url_and_node_id.json')
        data = extruct.extract(body, base_url='http://some-example.com',
                               syntaxes=['microdata'], return_html_node=True)
        replace_node_ref_with_node_id(data)
        self.assertEqual(data, expected)

    def test_deprecated_url(self):
        body, expected = self._microdata_custom_url('product_custom_url.json')
        with pytest.warns(DeprecationWarning):
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

    def test_errors(self):
        body = ''

        # raise exceptions
        with pytest.raises(Exception):
            data = extruct.extract(body)

        # ignore exceptions
        expected = {}
        data = extruct.extract(body, errors='ignore')
        assert data == expected

        # ignore exceptions
        data = extruct.extract(body, errors='log')
        assert data == expected
