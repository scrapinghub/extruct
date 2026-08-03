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


HTML_OR_JS_COMMENTLINE = re.compile(r"^\s*(//.*|<!--.*?-->)")


def parse_json(json_string):
    try:
        return json.loads(json_string, strict=False)
    except ValueError:
        pass

    # sometimes JSON-decoding errors are due to leading HTML or JavaScript comments
    json_string = HTML_OR_JS_COMMENTLINE.sub("", json_string)

    while True:
        try:
            return jstyleson.loads(json_string, strict=False)
        except json.JSONDecodeError as error:
            # unescaped quote inside a string value: escape it and retry
            if (
                error.msg == "Expecting ',' delimiter"
                and json_string[error.pos - 1] == '"'
            ):
                insertion_position = error.pos - 1
                prefix = json_string[:insertion_position]
                suffix = json_string[insertion_position:]
                json_string = prefix + "\\" + suffix
                continue
            raise


def parse_xmldom_html(html, encoding):
    """Parse HTML using XmlDomHTMLParser, return a tree"""
    parser = XmlDomHTMLParser(encoding=encoding)
    return lxml.html.fromstring(html, parser=parser)
