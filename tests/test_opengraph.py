# -*- coding: utf-8 -*-
import json
import unittest

from extruct.opengraph import OpenGraphExtractor
from tests import get_testdata, jsonize_dict


class TestOpengraph(unittest.TestCase):

    maxDiff = None

    def test_opengraph(self):
        body = get_testdata('misc', 'opengraph_test.html')
        expected = json.loads(get_testdata('misc', 'opengraph_test.json').decode('UTF-8'))

        opengraphe = OpenGraphExtractor()
        data = opengraphe.extract(body)
        self.assertEqual(jsonize_dict(data), expected)

    def test_opengraph_in_body(self):
        # OpenGraph tags are sometimes found in the body instead of (or
        # nested inside a wrapper element in) the head, e.g. when injected
        # dynamically by client-side code.
        body = get_testdata('misc', 'opengraph_body_test.html')
        expected = json.loads(
            get_testdata('misc', 'opengraph_body_test.json').decode('UTF-8'))

        opengraphe = OpenGraphExtractor()
        data = opengraphe.extract(body)
        self.assertEqual(jsonize_dict(data), expected)

    def test_opengraph_in_head_and_body(self):
        body = get_testdata('misc', 'opengraph_head_and_body_test.html')
        expected = json.loads(
            get_testdata('misc', 'opengraph_head_and_body_test.json').decode('UTF-8'))

        opengraphe = OpenGraphExtractor()
        data = opengraphe.extract(body)
        self.assertEqual(jsonize_dict(data), expected)
