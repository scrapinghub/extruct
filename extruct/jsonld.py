# -*- coding: utf-8 -*-
"""
JSON-LD extractor
"""

import json

import lxml.etree

from extruct.utils import parse_html, parse_json


class JsonLdExtractor(object):
    _xp_jsonld = lxml.etree.XPath('descendant-or-self::script[@type="application/ld+json"]')

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url=base_url)

    def extract_items(self, document, base_url=None):
        return [
            item
            for items in map(self._extract_items, self._xp_jsonld(document))
            if items for item in items if item
        ]

    def _extract_items(self, node):
        data = parse_json(node.xpath('string()'))
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
