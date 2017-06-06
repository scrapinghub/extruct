# -*- coding: utf-8 -*-
"""
JSON-LD extractor
"""

import json

import lxml.etree
import lxml.html


class JsonLdExtractor(object):
    _xp_jsonld = lxml.etree.XPath('descendant-or-self::script[@type="application/ld+json"]')

    def extract(self, htmlstring, url='http://www.example.com/', encoding="UTF-8"):
        parser = lxml.html.HTMLParser(encoding=encoding)
        lxmldoc = lxml.html.fromstring(htmlstring, parser=parser)
        return self.extract_items(lxmldoc)

    def extract_items(self, document, *args, **kwargs):
        return [item for items in map(self._extract_items,
                                      self._xp_jsonld(document))
                     for item in items
                         if item]

    def _extract_items(self, node):
        data = json.loads(node.xpath('string()'))
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
