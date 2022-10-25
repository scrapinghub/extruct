# -*- coding: utf-8 -*-
"""
JSON-LD extractor
"""

import json
import re

import jstyleson
import lxml.etree

from extruct.utils import parse_html

HTML_OR_JS_COMMENTLINE = re.compile(r'^\s*(//.*|<!--.*-->)')


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
        script = node.xpath('string()')
        script = self.clean_special_characters(script)
        try:
            # TODO: `strict=False` can be configurable if needed
            data = json.loads(script, strict=False)
        except ValueError:
            # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
            data = jstyleson.loads(HTML_OR_JS_COMMENTLINE.sub('', script), strict=False)
        if isinstance(data, list):
            for item in data:
                yield item
        elif isinstance(data, dict):
            yield data

    def clean_special_characters(self, script):
        special_character_dict = {
            '\\x27': "\'",
            '\\x22': '\"',
            '\\x3c': '<',
            '\\x3e': '>',
            '\\x2f': '/',
            '\\x5c': '\\',
            '\\x2a': '*',
            '\\x3d': '=',
            '\\x3f': '?',
            '\\x21': '!',
            '\\x7b': '{',
            '\\x7d': '}',
            '\\x7c': '|',
            '\\x5e': '^',
            '\\x60': '`',
            '\\x40': '@',
            '\\x23': '#',
            '\\x24': '$',
            '\\x25': '%',
            '\\x5b': '[',
            '\\x5d': ']',
            '\\x5f': '_',
            '\\x3a': ':',
            '\\x3b': ';',
            '\\x2c': ',',
            '\\x2e': '.',
            '\\x2d': '-',
            '\\x2b': '+',
        }
        for key, value in special_character_dict.items():
            script = script.replace(key, value)
        return script