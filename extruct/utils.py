# mypy: disallow_untyped_defs=False
import lxml.html

from extruct.xmldom import XmlDomHTMLParser


def _to_bytes(html, encoding):
    # lxml rejects str input that starts with an XML encoding declaration.
    if isinstance(html, str):
        return html.encode("utf-8"), "utf-8"
    return html, encoding


def parse_html(html, encoding):
    """Parse HTML using lxml.html.HTMLParser, return a tree"""
    html, encoding = _to_bytes(html, encoding)
    parser = lxml.html.HTMLParser(encoding=encoding)
    return lxml.html.fromstring(html, parser=parser)


def parse_xmldom_html(html, encoding):
    """Parse HTML using XmlDomHTMLParser, return a tree"""
    html, encoding = _to_bytes(html, encoding)
    parser = XmlDomHTMLParser(encoding=encoding)
    return lxml.html.fromstring(html, parser=parser)
