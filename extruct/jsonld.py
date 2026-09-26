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

HTML_OR_JS_COMMENTLINE = re.compile(r"^\s*(//.*|<!--.*-->)")

logger = logging.getLogger(__name__)


class JsonLdExtractor:
    _xp_jsonld = lxml.etree.XPath(
        'descendant-or-self::script[@type="application/ld+json"]'
    )

    def __init__(self, errors="strict"):
        """With *errors* set to ``"log"`` or ``"ignore"``, scripts that are not
        valid JSON are skipped, logging the error or not respectively, instead
        of raising an exception."""
        self._errors = errors

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url=base_url)

    def extract_items(self, document, base_url=None):
        return [
            item
            for items in map(self._extract_items, self._xp_jsonld(document))  # type: ignore[arg-type]
            if items
            for item in items
            if item
        ]

    def _extract_items(self, node):
        script = node.xpath("string()").strip()
        if not script:
            return
        try:
            data = self._load_json(script)
        except ValueError:
            if self._errors == "strict":
                raise
            if self._errors == "log":
                logger.exception(f"Skipping invalid JSON-LD: {script!r}")
            return
        if isinstance(data, list):
            yield from data
        elif isinstance(data, dict):
            yield data

    @staticmethod
    def _load_json(script):
        try:
            # TODO: `strict=False` can be configurable if needed
            return json.loads(script, strict=False)
        except ValueError:
            # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
            return jstyleson.loads(HTML_OR_JS_COMMENTLINE.sub("", script), strict=False)
