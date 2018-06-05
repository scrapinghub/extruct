# -*- coding: utf-8 -*-
import json
import unittest
from tests import get_testdata, jsonize_dict
import extruct


class TestFlatten(unittest.TestCase):

    maxDiff = None

    def test_microdata(self):
        body = get_testdata('schema.org', 'CreativeWork.001.html')
        expected = json.loads(get_testdata('schema.org', 'CreativeWork_flat.001.json').decode('UTF-8'))
        data = extruct.extract(body, uniform=True)
        self.assertEqual(jsonize_dict(data['microdata']), expected['microdata'])

    def test_microformat(self):
        body = get_testdata('misc', 'microformat_test.html')
        expected = json.loads(get_testdata('misc', 'microformat_flat_test.json').decode('UTF-8'))
        data = extruct.extract(body, uniform=True)
        self.assertEqual(jsonize_dict(data['microformat']), expected)
    
    def test_opengraph(self):
        body = get_testdata('misc', 'opengraph_test.html')
        expected = json.loads(get_testdata('misc', 'opengraph_flat_test.json').decode('UTF-8'))
        data = extruct.extract(body, uniform=True)
        self.assertEqual(jsonize_dict(data['opengraph']), expected)
