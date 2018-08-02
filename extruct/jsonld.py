# -*- coding: utf-8 -*-
"""
JSON-LD extractor
"""

import json
import re

import lxml.etree
import lxml.html


HTML_OR_JS_COMMENTLINE = re.compile('^\s*(//.*|<!--.*-->)')


class JsonLdExtractor(object):
    _xp_jsonld = lxml.etree.XPath('descendant-or-self::script[@type="application/ld+json"]')

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        parser = lxml.html.HTMLParser(encoding=encoding)
        lxmldoc = lxml.html.fromstring(htmlstring, parser=parser)
        return self.extract_items(lxmldoc, base_url=base_url)

    def extract_items(self, document, base_url=None):
        return [item for items in map(self._extract_items,
                                      self._xp_jsonld(document))
                     for item in items
                         if item]

    def _extract_items(self, node):
        script = node.xpath('string()')
        # now do remove possible leading HTML/JavaScript comment first, allow control characters to be loaded
        # TODO: `strict=False` can be configurable if needed
        data = json.loads(HTML_OR_JS_COMMENTLINE.sub('', script), strict=False)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
