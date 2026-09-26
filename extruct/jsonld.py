"""
JSON-LD extractor
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from typing import Any

import jstyleson
import lxml.etree
from lxml.html import HtmlElement

from extruct.utils import parse_html

HTML_OR_JS_COMMENTLINE = re.compile(r"^\s*(//.*|<!--.*-->)")


class JsonLdExtractor:
    _xp_jsonld = lxml.etree.XPath(
        'descendant-or-self::script[@type="application/ld+json"]'
    )

    def extract(
        self,
        htmlstring: str | bytes,
        base_url: str | None = None,
        encoding: str = "UTF-8",
    ) -> list[Any]:
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url=base_url)

    def extract_items(
        self, document: HtmlElement, base_url: str | None = None
    ) -> list[Any]:
        return [
            item
            for items in map(self._extract_items, self._xp_jsonld(document))
            if items
            for item in items
            if item
        ]

    def _extract_items(self, node: HtmlElement) -> Iterator[Any]:
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
