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

    def extract_items(self, document):
        return {"items" : [item
                           for item in map(self.extract_item,
                                           self._xp_jsonld(document))
                           if item]}

    def extract_item(self, node):
        return json.loads(node.xpath('string()'))
