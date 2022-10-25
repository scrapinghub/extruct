# -*- coding: utf-8 -*-
"""
JSON-LD extractor
"""

import json
import re

import jstyleson
import lxml.etree
import logging

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

    def _may_be_get_json(self, script):
        try:
            return json.loads(script, strict=False)
        except Exception:
            return None

    def _extract_items(self, node):
        script = node.xpath('string()')
        data = self._may_be_get_json(script)
        # check if valid json.
        if not data:
            # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
            script = jstyleson.dispose(HTML_OR_JS_COMMENTLINE.sub('', script))
            data = self._may_be_get_json(script)
        # After processing check if json is still valid.
        if not data:
            logging.exception('Invalid jsonld element detected %s', script)
            return

        if isinstance(data, list):
            for item in data:
                yield item
        elif isinstance(data, dict):
            yield data
