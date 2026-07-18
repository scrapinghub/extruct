# mypy: disallow_untyped_defs=False
"""
JSON-LD extractor
"""

import json
import logging
import re

import jstyleson
import lxml.etree

from extruct.utils import parse_html

logger = logging.getLogger(__name__)
HTML_OR_JS_COMMENTLINE = re.compile(r"^\s*(//.*|<!--.*-->)")


class JsonLdExtractor:
    _xp_jsonld = lxml.etree.XPath(
        'descendant-or-self::script[@type="application/ld+json"]'
    )

    def __init__(self, errors="strict"):
        self.errors = errors

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url=base_url)

    def extract_items(self, document, base_url=None):
        items = []
        for node in self._xp_jsonld(document):  # type: ignore[arg-type]
            try:
                for item in self._extract_items(node) or ():
                    if item:
                        items.append(item)
            except ValueError as e:
                if self.errors == "strict":
                    raise
                if self.errors == "log":
                    logger.exception(
                        "Failed to extract json-ld script, raises {}".format(e)
                    )
        return items

    def _extract_items(self, node):
        script = node.xpath("string()").strip()
        if not script:
            return
        try:
            # TODO: `strict=False` can be configurable if needed
            data = json.loads(script, strict=False)
        except ValueError:
            # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
            data = jstyleson.loads(HTML_OR_JS_COMMENTLINE.sub("", script), strict=False)
        if isinstance(data, list):
            yield from data
        elif isinstance(data, dict):
            yield data
