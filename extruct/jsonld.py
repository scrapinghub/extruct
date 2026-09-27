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

JSON_SPACE = " \t\r\n"


def _skip_space(script, index):
    while index < len(script) and script[index] in JSON_SPACE:
        index += 1
    return index


def _decode_leading_values(script):
    """Decode as many complete JSON values as ``script`` starts with.

    Pages sometimes append junk to an otherwise valid value (a stray closing
    brace, a stray semicolon), or concatenate several values in one script.
    Anything left over once no further value can be decoded is dropped.
    """
    decoder = json.JSONDecoder(strict=False)
    values = []
    index = _skip_space(script, 0)
    while index < len(script):
        try:
            value, index = decoder.raw_decode(script, index)
        except ValueError:
            break
        values.append(value)
        index = _skip_space(script, index)
    if values and index < len(script):
        logger.warning(
            "Ignoring {} trailing characters after the JSON-LD value".format(
                len(script) - index
            )
        )
    return values


def _iter_items(data):
    if isinstance(data, list):
        yield from data
    elif isinstance(data, dict):
        yield data


class JsonLdExtractor:
    _xp_jsonld = lxml.etree.XPath(
        'descendant-or-self::script[@type="application/ld+json"]'
    )

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
            # TODO: `strict=False` can be configurable if needed
            data = json.loads(script, strict=False)
        except ValueError:
            # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
            unwrapped = HTML_OR_JS_COMMENTLINE.sub("", script)
            try:
                data = jstyleson.loads(unwrapped, strict=False)
            except ValueError:
                # the script may still start with one or more valid values,
                # followed by trailing junk
                values = _decode_leading_values(unwrapped)
                if not values:
                    raise
                for value in values:
                    yield from _iter_items(value)
                return
        yield from _iter_items(data)
