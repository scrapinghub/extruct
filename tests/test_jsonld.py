# -*- coding: utf-8 -*-
import json
import unittest

from extruct.jsonld import JsonLdExtractor
from tests import get_testdata

class TestJsonLD(unittest.TestCase):

    def test_schemaorg_CreativeWork(self):
        body = get_testdata('schema.org', 'CreativeWork.001.html')
        expected = json.loads(get_testdata('schema.org', 'CreativeWork.001.jsonld').decode('UTF-8'))

        jsonlde = JsonLdExtractor()
        data = jsonlde.extract(body)
        self.assertEqual(data, expected)

    def test_songkick(self):
        page = "Elysian Fields Brooklyn Tickets, The Owl Music Parlor, 31 Oct 2015"
        body = get_testdata('songkick', '{}.html'.format(page))
        expected = json.loads(get_testdata('songkick', '{}.jsonld'.format(page)).decode('UTF-8'))

        jsonlde = JsonLdExtractor()
        data = jsonlde.extract(body)
        self.assertEqual(data, expected)

    def test_jsonld_with_comments(self):
        for prefix in ['JoinAction.001', 'AllocateAction.001']:
            body = get_testdata('schema.org.invalid', '{}.html'.format(prefix))
            name = '{}.jsonld'.format(prefix)
            expected = json.loads(get_testdata('schema.org.invalid', name).decode('UTF-8'))

            jsonlde = JsonLdExtractor()
            data = jsonlde.extract(body)
            self.assertEqual(data, expected)
        for prefix in ['JoinAction.001',
                       'AllocateAction.001',
                ]:
            body = get_testdata('custom.invalid', '{}.html'.format(prefix))
            expected = json.loads(get_testdata('custom.invalid', '{}.jsonld'.format(prefix)).decode('UTF-8'))

            jsonlde = JsonLdExtractor()
            data = jsonlde.extract(body)
            self.assertEqual(data, expected)

    def test_allow_control_characters(self):
        prefix = 'ControlCharacters'
        body = get_testdata('control.characters', '{}.html'.format(prefix))
        expected = json.loads(get_testdata('control.characters', '{}.jsonld'.format(prefix)).decode('UTF-8'))

        jsonlde = JsonLdExtractor()
        data = jsonlde.extract(body)
        self.assertEqual(data, expected)

    def test_allow_control_characters_exception(self):
        prefix = 'ControlCharacters'
        body = get_testdata('control.characters', '{}.html'.format(prefix))

        jsonlde = JsonLdExtractor(allow_control_characters=False)
        self.assertRaises(ValueError, jsonlde.extract, body)
