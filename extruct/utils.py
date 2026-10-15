# mypy: disallow_untyped_defs=False
import lxml.html

from extruct.xmldom import XmlDomHTMLParser


def _merge_trailing_html(root):
    # libxml2 puts content found after </html> into extra <html> siblings of
    # the root; move it into <body>, where HTML5 parsers put it.
    body = root.find("body")
    target = root if body is None else body
    for sibling in root.itersiblings(tag="html"):
        target.extend(sibling)
    return root


def parse_html(html, encoding):
    """Parse HTML using lxml.html.HTMLParser, return a tree"""
    parser = lxml.html.HTMLParser(encoding=encoding)
    return _merge_trailing_html(lxml.html.fromstring(html, parser=parser))


def parse_xmldom_html(html, encoding):
    """Parse HTML using XmlDomHTMLParser, return a tree"""
    parser = XmlDomHTMLParser(encoding=encoding)
    return _merge_trailing_html(lxml.html.fromstring(html, parser=parser))
