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

# An escape sequence, matched as a unit so that a "\\" pair is consumed whole
# and its second backslash cannot be mistaken for the start of another escape.
ESCAPE_SEQUENCE = re.compile(r"\\(u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)", re.S)
VALID_ESCAPE_CHARS = set('"\\/bfnrt')


def _repair_escape(match):
    escape = match.group(1)
    if len(escape) == 5 and escape[0] == "u":
        return match.group(0)  # \uXXXX, the only multi-character JSON escape
    if len(escape) == 3 and escape[0] == "x":
        # JavaScript hex escape; JSON only understands the \uXXXX form
        return "\\u00" + escape[1:]
    if escape in VALID_ESCAPE_CHARS:
        return match.group(0)
    if escape == "'":
        # a JavaScript habit; a single quote needs no escaping in JSON
        return escape
    # most likely a literal backslash that was never escaped, as in a Windows
    # path or a regular expression, so keep it rather than lose a character
    return "\\\\" + escape


def _repair_escapes(script):
    """Rewrite JavaScript escape sequences that JSON does not allow.

    ``\\'`` becomes ``'`` and ``\\x27`` becomes ``\\u0027``. Any other
    backslash is treated as a literal that should have been escaped, and is
    doubled rather than dropped. Valid escapes are left untouched, so this is
    a no-op on well-formed JSON.
    """
    return ESCAPE_SEQUENCE.sub(_repair_escape, script)


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
                # invalid escape sequences such as \' or \x27 come from
                # JavaScript string literals finding their way into JSON
                repaired = _repair_escapes(unwrapped)
                try:
                    data = jstyleson.loads(repaired, strict=False)
                except ValueError:
                    # the script may still start with one or more valid values,
                    # followed by trailing junk
                    values = _decode_leading_values(repaired)
                    if not values:
                        raise
                    for value in values:
                        yield from _iter_items(value)
                    return
        yield from _iter_items(data)
