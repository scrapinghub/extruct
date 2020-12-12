"""
HTML Microdata parser

Piece of code extracted form:
* http://blog.scrapinghub.com/2014/06/18/extracting-schema-org-microdata-using-scrapy-selectors-and-xpath/

follows http://www.w3.org/TR/microdata/#json

"""

import collections
from functools import partial
from xml.sax.saxutils import unescape

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

from bleach_extras import cleaner_factory__strip_content as Cleaner
from bleach.sanitizer import (
    ALLOWED_TAGS,
    ALLOWED_ATTRIBUTES,
)
from html5lib.filters.whitespace import collapse_spaces
from w3lib.html import strip_html5_whitespace
import xpath

from extruct.utils import parse_html


cleaner = Cleaner(
    tags=[],
    attributes=ALLOWED_ATTRIBUTES,
    styles=[],
    protocols=[],
    strip=True,
    strip_comments=True
)


class MicrodataExtractor(object):
    # iterate in document order (used below for fast get_docid)
    _xp_item = 'descendant-or-self::*[@itemscope]'
    _xp_prop = './/*[@itemprop]'
    _xp_scope = './/*[@itemscope]//*[@itemprop]'
    _xp_clean_text = 'descendant-or-self::*[not(self::script or self::style)]/text()'

    def __init__(self, nested=True, strict=False, add_text_content=False, add_html_node=False):
        self.nested = nested
        self.strict = strict
        self.add_text_content = add_text_content
        self.add_html_node = add_html_node

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url)

    def extract_items(self, document, base_url):
        itemids = self._build_itemids(document)
        items_seen = set()
        items = [
            item for item in (
                self._extract_item(
                    it, items_seen=items_seen, base_url=base_url, itemids=itemids)
                for it in xpath.find(self._xp_item, document))
            if item]
        return items

    def get_docid(self, node, itemids):
        return itemids[node]

    def _build_itemids(self, document):
        """ Build itemids for a fast get_docid implementation. Use document order.
        """
        return {node: idx + 1 for idx, node in enumerate(xpath.find(self._xp_item, document))}

    def _extract_item(self, node, items_seen, base_url, itemids):
        itemid = self.get_docid(node, itemids)

        if self.nested:
            if itemid in items_seen:
                return
            items_seen.add(itemid)

        item = {}
        if not self.nested:
            item["iid"] = itemid
        types = node.getAttribute('itemtype').split()
        if types:
            if not self.strict and len(types) == 1:
                item["type"] = types[0]
            else:
                item["type"] = types

            nodeid = node.getAttribute('itemid')
            if nodeid:
                item["id"] = nodeid.strip()

        properties = collections.defaultdict(list)
        for name, value in self._extract_properties(
                node, items_seen=items_seen, base_url=base_url, itemids=itemids):
            properties[name].append(value)

        # process item references
        refs = node.getAttribute('itemref').split()
        if refs:
            for refid in refs:
                for name, value in self._extract_property_refs(
                        node, refid, items_seen=items_seen, base_url=base_url,
                        itemids=itemids):
                    properties[name].append(value)

        props = []
        for (name, values) in properties.items():
            if not self.strict and len(values) == 1:
                props.append((name, values[0]))
            else:
                props.append((name, values))
        if props:
            item["properties"] = dict(props)
        else:
            # item without properties; let's use the node itself
            item["value"] = self._extract_property_value(
                node, force=True, items_seen=items_seen, base_url=base_url,
                itemids=itemids)

        # below are not in the specs, but can be handy
        if self.add_text_content:
            textContent = self._extract_textContent(node)
            if textContent:
                item["textContent"] = textContent
        if self.add_html_node:
            item["htmlNode"] = node

        return item

    def _extract_properties(self, node, items_seen, base_url, itemids):
        scopes = set()
        for scope in xpath.find(self._xp_scope, node):
            scopes.add(scope)
        for prop in xpath.find(self._xp_prop, node):
            if prop in scopes:
                continue
            for p, v in self._extract_property(
                    prop, items_seen=items_seen, base_url=base_url, itemids=itemids):
                yield p, v

    def _extract_property_refs(self, node, refid, items_seen, base_url, itemids):
        ctx = xpath.XPathContext(variables={'refid': refid})
        ref_node = ctx.find("//*[@id=$refid][1]", node)
        if not ref_node:
            return
        ref_node = ref_node[0]
        extract_fn = partial(self._extract_property, items_seen=items_seen,
                             base_url=base_url, itemids=itemids)
        if 'itemprop' in ref_node.attributes and 'itemscope' in ref_node.attributes:
            # An full item will be extracted from the node, no need to look
            # for individual properties in child nodes
            for p, v in extract_fn(ref_node):
                yield p, v
        else:
            base_parent_scope = xpath.find("ancestor-or-self::*[@itemscope][1]", ref_node)
            for prop in xpath.find("descendant-or-self::*[@itemprop]", ref_node):
                parent_scope = xpath.find("ancestor::*[@itemscope][1]", prop)
                # Skip properties defined in a different scope than the ref_node
                if parent_scope == base_parent_scope:
                    for p, v in extract_fn(prop):
                        yield p, v

    def _extract_property(self, node, items_seen, base_url, itemids):
        props = node.getAttribute("itemprop").split()
        value = self._extract_property_value(
            node, items_seen=items_seen, base_url=base_url, itemids=itemids)
        return [(p, value) for p in props]

    def _extract_property_value(self, node, items_seen, base_url, itemids, force=False):
        #http://www.w3.org/TR/microdata/#values
        if not force and 'itemscope' in node.attributes:
            if self.nested:
                return self._extract_item(
                    node, items_seen=items_seen, base_url=base_url, itemids=itemids)
            else:
                return {"iid_ref": self.get_docid(node, itemids)}

        elif node.tagName == "meta":
            return node.getAttribute("content")

        elif node.tagName in ("audio", "embed", "iframe", "img", "source", "track", "video"):
            return urljoin(base_url, strip_html5_whitespace(node.getAttribute("src")))

        elif node.tagName in ("a", "area", "link"):
            return urljoin(base_url, strip_html5_whitespace(node.getAttribute("href")))

        elif node.tagName in ("object",):
            return urljoin(base_url, strip_html5_whitespace(node.getAttribute("data")))

        elif node.tagName in ("data", "meter"):
            return node.getAttribute("value")

        elif node.tagName in ("time",):
            return node.getAttribute("datetime")

        # not in W3C specs but used in schema.org examples
        elif "content" in node.attributes:
            return node.getAttribute("content")

        else:
            text = self._extract_textContent(node)
            return collapse_spaces(text)

    def _extract_textContent(self, node):
        clean_text = cleaner.clean(node.toxml()).strip()
        return unescape(clean_text)
