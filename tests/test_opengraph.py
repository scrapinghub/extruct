# -*- coding: utf-8 -*-
import json
import unittest

from extruct.opengraph import OpenGraphExtractor
from tests import get_testdata, jsonize_dict


class TestOpengraph(unittest.TestCase):

    maxDiff = None

    def _test_opengraph(self, name):
        body = get_testdata('misc', name + '.html')
        expected = json.loads(get_testdata('misc', name + '.json').decode('UTF-8'))

        opengraphe = OpenGraphExtractor()
        data = opengraphe.extract(body)
        self.assertEqual(jsonize_dict(data), expected)

    def test_opengraph(self):
        self._test_opengraph('opengraph_test')

    def test_opengraph_ns_product(self):
        self._test_opengraph('opengraph_ns_product_test')
