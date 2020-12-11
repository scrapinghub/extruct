# -*- coding: utf-8 -*-
"""
JSON-LD extractor
"""

import json
import re

import jstyleson
from xpath import XPathContext

from extruct.utils import parse_html

# TODO: is there a better way to identify the default namespace?
xpath = XPathContext(default_namespace='http://www.w3.org/1999/xhtml')

HTML_OR_JS_COMMENTLINE = re.compile(r'^\s*(//.*|<!--.*-->)')


class JsonLdExtractor(object):
    _xp_jsonld = 'descendant-or-self::script[@type="application/ld+json"]'

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url=base_url)

    def extract_items(self, document, base_url=None):
        return [
            item
            for items in map(self._extract_items, xpath.find(self._xp_jsonld, document))
            if items for item in items if item
        ]

    def _extract_items(self, node):
        script = xpath.find('string()', node)
        try:
            # TODO: `strict=False` can be configurable if needed
            data = json.loads(script, strict=False)
        except ValueError:
            # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
            data = jstyleson.loads(HTML_OR_JS_COMMENTLINE.sub('', script),strict=False)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
