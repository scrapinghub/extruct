from __future__ import annotations

import lxml.html

from extruct.xmldom import XmlDomHTMLParser


def parse_html(html: str | bytes, encoding: str) -> lxml.html.HtmlElement:
    """Parse HTML using lxml.html.HTMLParser, return a tree"""
    parser = lxml.html.HTMLParser(encoding=encoding)
    return lxml.html.fromstring(html, parser=parser)


def parse_xmldom_html(html: str | bytes, encoding: str) -> lxml.html.HtmlElement:
    """Parse HTML using XmlDomHTMLParser, return a tree"""
    parser = XmlDomHTMLParser(encoding=encoding)
    return lxml.html.fromstring(html, parser=parser)
