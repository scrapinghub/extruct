# -*- coding: utf-8 -*-
import json
import unittest

import extruct
from tests import get_testdata


class TestGeneric(unittest.TestCase):

    maxDiff = None

    def test_all(self):
        body = get_testdata('songkick', 'elysianfields.html')
        expected = json.loads(get_testdata('songkick', 'elysianfields.json').decode('UTF-8'))

        data = extruct.extract(body, 'http://www.songkick.com/artists/236156-elysian-fields')
        self.assertEqual(data, expected)
