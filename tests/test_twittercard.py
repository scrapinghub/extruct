# -*- coding: utf-8 -*-
import json
import unittest

from extruct.twittercard import TwitterCardExtractor
from tests import get_testdata, jsonize_dict

class TestTwittercard(unittest.TestCase):
    maxDiff = None

    def _test_twittercard(self, name):
        body = get_testdata('misc', name + '.html')
        expected = json.loads(get_testdata('misc', name + '.json').decode('UTF-8'))

        twittercard = TwitterCardExtractor()
        data = twittercard.extract(body)
        self.assertEqual(jsonize_dict(data), expected)

    def twittercard_spinneyslebanon_test(self):
        self._test_twittercard('twittercard_spinneyslebanon_test')
    
    def twittercard_optimizesmart_test(self):
        self._test_twittercard('twittercard_optimizesmart_test')

    def twittercard_chess_test(self):
        self._test_twittercard('twittercard_chess_test')
    
