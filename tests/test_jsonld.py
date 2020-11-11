# -*- coding: utf-8 -*-
import json
import unittest

from extruct.jsonld import JsonLdExtractor
from tests import get_testdata


class TestJsonLD(unittest.TestCase):

    def test_schemaorg_CreativeWork(self):
        self.assertJsonLdCorrect(folder='schema.org', page='CreativeWork.001')

    def test_songkick(self):
        self.assertJsonLdCorrect(
            folder='songkick',
            page=
            'Elysian Fields Brooklyn Tickets, The Owl Music Parlor, 31 Oct 2015'
        )

    def test_jsonld_empty_item(self):
        self.assertJsonLdCorrect(
            folder='songkick',
            page='jsonld_empty_item_test'
        )

    def test_jsonld_with_comments(self):
        for page in ['JoinAction.001', 'AllocateAction.001']:
            self.assertJsonLdCorrect(folder='schema.org.invalid', page=page)

        for page in ['JoinAction.001', 'AllocateAction.001']:
            self.assertJsonLdCorrect(folder='custom.invalid', page=page)

    def test_jsonld_with_control_characters(self):
        self.assertJsonLdCorrect(
            folder='custom.invalid',
            page='JSONLD_with_control_characters')

    def test_jsonld_with_control_characters_comment(self):
        self.assertJsonLdCorrect(
            folder='custom.invalid',
            page='JSONLD_with_control_characters_comment')
        
    def test_jsonld_with_json_including_js_comment(self):
        self.assertJsonLdCorrect(
            folder='custom.invalid',
            page='JSONLD_with_JS_comment')

    def assertJsonLdCorrect(self, folder, page):
        body, expected = self._get_body_expected(folder, page)
        self._check_jsonld(body, expected)

    def _get_body_expected(self, folder, page):
        body = get_testdata(folder, '{}.html'.format(page))
        expected = get_testdata(folder, '{}.jsonld'.format(page))
        return body, json.loads(expected.decode('utf8'))

    def _check_jsonld(self, body, expected):
        jsonlde = JsonLdExtractor()
        data = jsonlde.extract(body)
        self.assertEqual(data, expected)
