# mypy: disallow_untyped_defs=False
import json
import re

import jstyleson
import lxml.html

from extruct.xmldom import XmlDomHTMLParser


def parse_html(html, encoding):
    """Parse HTML using lxml.html.HTMLParser, return a tree"""
    parser = lxml.html.HTMLParser(encoding=encoding)
    return lxml.html.fromstring(html, parser=parser)


_HTML_COMMENTLINE = re.compile(r"^\s*<!--.*?-->")


def _parse_json(json_string):
    try:
        return json.loads(json_string, strict=False)
    except ValueError:
        pass

    # Comments are stripped once, up front: the error offsets used below must
    # refer to the same string that json.loads() reads. jstyleson.dispose()
    # handles JavaScript comments and trailing commas, but not HTML comments.
    json_string = jstyleson.dispose(_HTML_COMMENTLINE.sub("", json_string))

    # Each iteration escapes one quote and never adds one, so the loop runs at
    # most as many times as there are quotes in the string.
    while True:
        try:
            return json.loads(json_string, strict=False)
        except json.JSONDecodeError as error:
            # An unescaped double quote inside a string value ends that value
            # early, so the parser finds text where it expects the next item.
            # Escape the quote that ended the value and try again. The reported
            # position is past any whitespace that follows the quote.
            quote = json_string.rfind('"', 0, error.pos)
            if (
                error.msg != "Expecting ',' delimiter"
                or quote < 0
                or json_string[quote + 1 : error.pos].strip()
            ):
                raise
            json_string = json_string[:quote] + "\\" + json_string[quote:]


def parse_xmldom_html(html, encoding):
    """Parse HTML using XmlDomHTMLParser, return a tree"""
    parser = XmlDomHTMLParser(encoding=encoding)
    return lxml.html.fromstring(html, parser=parser)
