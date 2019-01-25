# -*- coding: utf-8 -*-
"""
JSON-LD extractor
"""

import json
import re

import lxml.etree

from extruct.utils import parse_html

HTML_OR_JS_COMMENTLINE = re.compile(r'^\s*(//.*|<!--.*-->)')


class JsonLdExtractor(object):
    _xp_jsonld = lxml.etree.XPath('descendant-or-self::script[@type="application/ld+json"]')

    def extract(self, htmlstring, base_url=None, encoding="UTF-8", as_json=False):
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url=base_url, as_json=as_json)

    def extract_items(self, document, base_url=None, as_json=False):
        return [
            item
            for items in map(self._extract_items_raw if as_json else self.extract_items, self._xp_jsonld(document))
            if items for item in items if item
        ]

    def _extract_items_raw(self, node):
        return HTML_OR_JS_COMMENTLINE.sub('', node.xpath('string()'))

    def _extract_items(self, node):
        script = self._extract_items_raw(node)
        # TODO: `strict=False` can be configurable if needed
        data = json.loads(script, strict=False)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
