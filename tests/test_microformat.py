# -*- coding: utf-8 -*-
import json
import unittest

from extruct.microformat import MicroformatExtractor
from tests import get_testdata, jsonize_dict


class TestJsonLD(unittest.TestCase):

    maxDiff = None

    def test_schemaorg_CreativeWork(self):
        body = get_testdata('misc', 'microformat_test.html')
        expected = json.loads(get_testdata('misc', 'microformat_test.json').decode('UTF-8'))

        opengraphe = MicroformatExtractor()
        data = opengraphe.extract(body)
        self.assertEqual(jsonize_dict(data), expected)
