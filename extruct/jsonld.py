# -*- coding: utf-8 -*-
"""
JSON-LD extractor
"""

import json
import re

import lxml.etree

from extruct.utils import parse_html


class JsonLdExtractor(object):
    _xp_jsonld = lxml.etree.XPath(
        'descendant-or-self::script[@type="application/ld+json"]')

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url=base_url)

    def extract_items(self, document, base_url=None):
        return [
            item
            for items in map(self._extract_items, self._xp_jsonld(document))
            if items for item in items if item
        ]

    def _extract_json_objects(self, text, decoder=json.JSONDecoder()):
        """Find JSON objects in text, and yield the decoded JSON data

        Does not attempt to look for JSON arrays, text, or other JSON types outside
        of a parent JSON object.

        """
        pos = 0
        while True:
            match = text.find('{', pos)
            if match == -1:
                break
            try:
                result, index = decoder.raw_decode(text[match:])
                yield result
                pos = match + index
            except ValueError:
                pos = match + 1

    def _extract_items(self, node):
        script = node.xpath('string()')

        try:
            # TODO: `strict=False` can be configurable if needed
            data = json.loads(script, strict=False)
        except ValueError:
            # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
            data = []
            try:
                text = str(script)
                for result in self._extract_json_objects(text):
                    if result:
                        data.append(result)
            except:
                return None

        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
