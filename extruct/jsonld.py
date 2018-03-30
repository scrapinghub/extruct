# -*- coding: utf-8 -*-
"""
JSON-LD extractor
"""

from extruct import utils
import re

import lxml.etree
import lxml.html


HTML_OR_JS_COMMENTLINE = re.compile('^\s*(//.*|<!--.*-->)')

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
        script = node.xpath('string()')
        try:
            data = utils.json_loads(script)
        except utils.native_json_exc:
            # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
            data = utils.json_loads(HTML_OR_JS_COMMENTLINE.sub('', script))
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
