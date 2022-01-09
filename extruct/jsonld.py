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

    def _is_valid_json(self, script):
        try:
            json.loads(script)
            return True
        except Exception:
            return False

    def _extract_items(self, node):
        script = node.xpath('string()')
        # check if valid json.
        if not self._is_valid_json(script):
            script = jstyleson.dispose( HTML_OR_JS_COMMENTLINE.sub('', script))
        # After processing check if json is still valid.
        if not self._is_valid_json(script):
            return False

        # if its valid then process the data.
        data = json.loads(script, strict=False)
        if isinstance(data, list):
            for item in data:
                yield item
        elif isinstance(data, dict):
            yield data
