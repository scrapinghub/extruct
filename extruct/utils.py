# mypy: disallow_untyped_defs=False
import lxml.html

from extruct.xmldom import XmlDomHTMLParser


def _clean_html(html):
    if isinstance(html, bytes):
        html = html.replace(b"\x00", b"")
        return html if html.strip() else b"<html/>"
    html = html.replace("\x00", "")
    return html if html.strip() else "<html/>"


def parse_html(html, encoding):
    """Parse HTML using lxml.html.HTMLParser, return a tree"""
    parser = lxml.html.HTMLParser(encoding=encoding)
    return lxml.html.fromstring(_clean_html(html), parser=parser)


def parse_xmldom_html(html, encoding):
    """Parse HTML using XmlDomHTMLParser, return a tree"""
    parser = XmlDomHTMLParser(encoding=encoding)
    return lxml.html.fromstring(_clean_html(html), parser=parser)
