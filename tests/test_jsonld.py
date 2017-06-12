# -*- coding: utf-8 -*-
import json
import unittest

from extruct.jsonld import JsonLdExtractor
from tests import get_testdata

class TestJsonLD(unittest.TestCase):

    maxDiff = None

    def test_schemaorg_CreativeWork(self):
        for i in [1]:
            body = get_testdata('schema.org', 'CreativeWork.{:03d}.html'.format(i))
            expected = json.loads(get_testdata('schema.org', 'CreativeWork.{:03d}.jsonld'.format(i)).decode('UTF-8'))

            jsonlde = JsonLdExtractor()
            data = jsonlde.extract(body)
            self.assertEqual(data, expected)

    def test_songkick(self):
        for page in [
                "Elysian Fields Brooklyn Tickets, The Owl Music Parlor, 31 Oct 2015",
                #"Maxïmo Park Gigography, Tour History & Past Concerts",
                #"Years & Years Tickets, Tour Dates 2015 & Concerts",
            ]:
            body = get_testdata('songkick', '{}.html'.format(page))
            expected = json.loads(get_testdata('songkick', '{}.jsonld'.format(page)).decode('UTF-8'))

            jsonlde = JsonLdExtractor()
            data = jsonlde.extract(body)
            self.assertEqual(data, expected)

    def test_jsonld_with_comments(self):
        for prefix in ['JoinAction.001',
                       'AllocateAction.001',
                ]:
            body = get_testdata('schema.org.invalid', '{}.html'.format(prefix))
            expected = json.loads(get_testdata('schema.org.invalid', '{}.jsonld'.format(prefix)).decode('UTF-8'))

            jsonlde = JsonLdExtractor()
            data = jsonlde.extract(body)
            self.assertEqual(data, expected)
