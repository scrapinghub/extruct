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
_ESCAPE_SEQUENCE = re.compile(r"\\(u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)", re.S)
_VALID_ESCAPE_CHARS = set('"\\/bfnrt')


def _repair_escape(match):
    escape = match.group(1)
    if len(escape) == 5 and escape[0] == "u":
        return match.group(0)  # \uXXXX, the only multi-character JSON escape
    if len(escape) == 3 and escape[0] == "x":
        # JavaScript hex escape; JSON only understands the \uXXXX form
        return "\\u00" + escape[1:]
    if escape in _VALID_ESCAPE_CHARS:
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
    return _ESCAPE_SEQUENCE.sub(_repair_escape, script)


JSON_SPACE = " \t\r\n"


_STRUCTURAL_CHARS = set(",}]:")


def _skip_space(script, index):
    while index < len(script) and script[index] in JSON_SPACE:
        index += 1
    return index


def _repair_quotes(script):
    """Escape double quotes that appear inside a JSON string.

    A quote is taken to close the string only when the next non-space
    character is structural; anywhere else it is content that the page failed
    to escape. A quote that does sit right before a structural character is
    still read as the end of the string, so this can truncate a value, but it
    cannot alter well-formed JSON, where every closing quote is followed by a
    structural character.
    """
    out = []
    index = 0
    length = len(script)
    in_string = False
    while index < length:
        char = script[index]
        if not in_string:
            out.append(char)
            in_string = char == '"'
            index += 1
        elif char == "\\" and index + 1 < length:
            # an escape sequence, consumed whole
            out.append(script[index : index + 2])
            index += 2
        elif char == '"':
            lookahead = _skip_space(script, index + 1)
            if lookahead >= length or script[lookahead] in _STRUCTURAL_CHARS:
                out.append(char)
                in_string = False
            else:
                out.append('\\"')
            index += 1
        else:
            out.append(char)
            index += 1
    return "".join(out)


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
                    # quotes left unescaped inside a string value, which can
                    # only be told apart from the end of the string by guessing
                    requoted = _repair_quotes(repaired)
                    try:
                        data = jstyleson.loads(requoted, strict=False)
                    except ValueError:
                        # the script may still start with one or more valid
                        # values, followed by trailing junk
                        values = _decode_leading_values(requoted)
                        if not values:
                            raise
                        for value in values:
                            yield from _iter_items(value)
                        return
                    # reached only when the guess changed something, since the
                    # unaltered text has already failed above
                    logger.warning(
                        "Guessed which quotes a JSON-LD script left unescaped"
                    )
        yield from _iter_items(data)
