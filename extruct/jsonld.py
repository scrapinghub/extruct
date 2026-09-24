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

# Framing that pages use to hide JSON-LD from HTML/XML parsers: HTML comments,
# CDATA sections, and the JavaScript line comments that often accompany them.
FRAMING_TOKENS = re.compile(r"//|/\*|\*/|<!--|-->|<!\[CDATA\[|\]\]>|\s+")


def _is_framing_line(line):
    """Whether a line consists only of wrapper framing and whitespace."""
    return not FRAMING_TOKENS.sub("", line)


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


STRUCTURAL_CHARS = set(",}]:")
JSON_SPACE = " \t\r\n"


def _skip_space(script, index):
    while index < len(script) and script[index] in JSON_SPACE:
        index += 1
    return index


def _repair_quotes(script):
    """Escape double quotes that appear inside a JSON string.

    A quote is taken to close the string only when the next non-space
    character is structural; anywhere else it is content that the page failed
    to escape. That is a guess, and an unescaped quote which happens to sit
    right before a structural character is still read as the end of the
    string. It cannot alter well-formed JSON though, where every closing
    quote is followed by a structural character.
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
            lookahead = index + 1
            while lookahead < length and script[lookahead] in JSON_SPACE:
                lookahead += 1
            if lookahead >= length or script[lookahead] in STRUCTURAL_CHARS:
                out.append(char)
                in_string = False
            else:
                out.append('\\"')
            index += 1
        else:
            out.append(char)
            index += 1
    return "".join(out)


def _repair_escapes(script):
    """Rewrite JavaScript escape sequences that JSON does not allow.

    ``\\'`` becomes ``'`` and ``\\x27`` becomes ``\\u0027``. Any other
    backslash is treated as a literal that should have been escaped, and is
    doubled rather than dropped. Valid escapes are left untouched, so this is
    a no-op on well-formed JSON.
    """
    return ESCAPE_SEQUENCE.sub(_repair_escape, script)


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


def _strip_framing(script):
    """Drop wrapper framing lines from both ends of a script.

    Only whole lines are removed, and only from the ends, so that ``//``
    sequences inside JSON string values are left alone.
    """
    lines = script.splitlines()
    start, end = 0, len(lines)
    while start < end and _is_framing_line(lines[start]):
        start += 1
    while end > start and _is_framing_line(lines[end - 1]):
        end -= 1
    return "\n".join(lines[start:end])


class JsonLdExtractor:
    _xp_jsonld = lxml.etree.XPath(
        'descendant-or-self::script[@type="application/ld+json"]'
    )

    def __init__(self, errors="strict"):
        """errors: set to 'log' to log the exceptions, 'ignore' to ignore them
        or 'strict'(default) to raise them. Applied per script element, so
        that one unparsable script does not discard the valid ones."""
        if errors not in ["log", "ignore", "strict"]:
            raise ValueError(
                'Invalid error command, valid values are either "log"'
                ', "ignore" or "strict"'
            )
        self.errors = errors

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url=base_url)

    def extract_items(self, document, base_url=None):
        items = []
        for node in self._xp_jsonld(document):  # type: ignore[union-attr]
            try:
                # Parsed eagerly, so that a failure discards only this script.
                parsed = [item for item in self._extract_items(node) if item]
            except ValueError as e:
                if self.errors == "strict":
                    raise
                if self.errors == "log":
                    logger.exception(
                        "Failed to parse JSON-LD script, raises {}".format(e)
                    )
                continue
            items.extend(parsed)
        return items

    def _extract_items(self, node):
        script = node.xpath("string()").strip()
        if not script:
            return []
        return self._parse_items(script)

    def _parse_items(self, script):
        """Parse one script element into a list of JSON-LD items.

        Malformed markup is worked around in increasingly lenient steps, each
        only reached once the previous one has failed.
        """
        try:
            # TODO: `strict=False` can be configurable if needed
            return list(_iter_items(json.loads(script, strict=False)))
        except ValueError as e:
            # kept so that the failure reported is the one of the unaltered
            # markup, rather than the one of a repair attempted below
            error = e

        # sometimes JSON-decoding errors are due to leading HTML or JavaScript
        # comments, or to the CDATA/comment framing used to hide JSON-LD from
        # HTML parsers
        unwrapped = HTML_OR_JS_COMMENTLINE.sub("", _strip_framing(script))
        # invalid escape sequences such as \' or \x27 come from JavaScript
        # string literals finding their way into JSON
        repaired = _repair_escapes(unwrapped)

        # quotes left unescaped inside a string value, which can only be told
        # apart from the end of the string by guessing
        requoted = _repair_quotes(repaired)

        # each candidate is tried only once the plainer ones have failed
        candidates = [(unwrapped, "")]
        if repaired != unwrapped:
            candidates.append((repaired, ""))
        if requoted != repaired:
            candidates.append(
                (requoted, "Guessed which quotes a JSON-LD script left unescaped")
            )

        for candidate, guess in candidates:
            try:
                # jstyleson only strips a "//" comment that is terminated by a
                # newline, and the trailing one was removed above
                data = jstyleson.loads(candidate + "\n", strict=False)
            except ValueError:
                continue
            if guess:
                logger.warning(guess)
            return list(_iter_items(data))

        # the script may still start with one or more valid values, followed
        # by trailing junk
        values = _decode_leading_values(candidates[-1][0])
        if not values:
            raise error
        return [item for value in values for item in _iter_items(value)]
