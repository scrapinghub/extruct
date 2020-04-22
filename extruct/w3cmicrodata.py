"""
HTML Microdata parser

Piece of code extracted form:
* http://blog.scrapinghub.com/2014/06/18/extracting-schema-org-microdata-using-scrapy-selectors-and-xpath/

Ported to lxml
follows http://www.w3.org/TR/microdata/#json

"""

import collections
from functools import partial

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

import lxml.etree
from lxml.html.clean import Cleaner
from w3lib.html import strip_html5_whitespace
import html_text

from extruct.utils import parse_html


# Cleaner which is similar to html_text cleaner, but is less aggressive
cleaner = Cleaner(
    scripts=True,
    javascript=False,  # onclick attributes are fine
    comments=True,
    style=True,
    links=False,  # e.g. availability is included in <link> tags
    meta=False,  # some sites use <meta> tags in body to provide property
    page_structure=False,  # <title> may be nice to have
    processing_instructions=True,
    embedded=False,  # keep embedded content
    frames=False,  # keep frames
    forms=False,  # keep forms
    annoying_tags=False,
    remove_unknown_tags=False,
    safe_attrs_only=False,
)


class LxmlMicrodataExtractor(object):
    _xp_item = lxml.etree.XPath('descendant-or-self::*[@itemscope]')
    _xp_prop = lxml.etree.XPath("""set:difference(.//*[@itemprop],
                                                  .//*[@itemscope]//*[@itemprop])""",
                                namespaces = {"set": "http://exslt.org/sets"})
    # ancestor and preceding axes contain all elements before the context node
    # so counting them gives the "document order" of the context node
    _xp_item_docid = lxml.etree.XPath("""count(preceding::*[@itemscope])
                                       + count(ancestor::*[@itemscope])
                                       + 1""")

    def __init__(self, nested=True, strict=False, add_text_content=False, add_html_node=False):
        self.nested = nested
        self.strict = strict
        self.add_text_content = add_text_content
        self.add_html_node = add_html_node

    def get_docid(self, node):
        return int(self._xp_item_docid(node))

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        tree = parse_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url)

    def extract_items(self, document, base_url):
        cleaned_document = cleaner.clean_html(document)
        items_seen = set()
        return [
            item for item in (
                self._extract_item(it, items_seen=items_seen, base_url=base_url)
                for it in self._xp_item(cleaned_document))
            if item]

    def _extract_item(self, node, items_seen, base_url):
        itemid = self.get_docid(node)

        if self.nested:
            if itemid in items_seen:
                return
            items_seen.add(itemid)

        item = {}
        if not self.nested:
            item["iid"] = itemid
        types = node.get('itemtype', '').split()
        if types:
            if not self.strict and len(types) == 1:
                item["type"] = types[0]
            else:
                item["type"] = types

            itemid = node.get('itemid')
            if itemid:
                item["id"] = itemid.strip()

        properties = collections.defaultdict(list)
        for name, value in self._extract_properties(
                node, items_seen=items_seen, base_url=base_url):
            properties[name].append(value)

        # process item references
        refs = node.get('itemref', '').split()
        if refs:
            for refid in refs:
                for name, value in self._extract_property_refs(
                        node, refid, items_seen=items_seen, base_url=base_url):
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
                node, force=True, items_seen=items_seen, base_url=base_url)

        # below are not in the specs, but can be handy
        if self.add_text_content:
            textContent = self._extract_textContent(node)
            if textContent:
                item["textContent"] = textContent
        if self.add_html_node:
            item["htmlNode"] = node

        return item

    def _extract_properties(self, node, items_seen, base_url):
        for prop in self._xp_prop(node):
            for p, v in self._extract_property(
                    prop, items_seen=items_seen, base_url=base_url):
                yield p, v

    def _extract_property_refs(self, node, refid, items_seen, base_url):
        ref_node = node.xpath("id($refid)[1]", refid=refid)
        if not ref_node:
            return
        ref_node = ref_node[0]
        extract_fn = partial(self._extract_property, items_seen=items_seen,
                             base_url=base_url)
        if 'itemprop' in ref_node.keys() and 'itemscope' in ref_node.keys():
            # An full item will be extracted from the node, no need to look
            # for individual properties in childs
            for p, v in extract_fn(ref_node):
                yield p, v
        else:
            base_parent_scope = ref_node.xpath("ancestor-or-self::*[@itemscope][1]")
            for prop in ref_node.xpath("descendant-or-self::*[@itemprop]"):
                parent_scope = prop.xpath("ancestor::*[@itemscope][1]")
                # Skip properties defined in a different scope than the ref_node
                if parent_scope == base_parent_scope:
                    for p, v in extract_fn(prop):
                        yield p, v

    def _extract_property(self, node, items_seen, base_url):
        props = node.get("itemprop").split()
        value = self._extract_property_value(
            node, items_seen=items_seen, base_url=base_url)
        return [(p, value) for p in props]

    def _extract_property_value(self, node, items_seen, base_url, force=False):
        #http://www.w3.org/TR/microdata/#values
        if not force and node.get("itemscope") is not None:
            if self.nested:
                return self._extract_item(
                    node, items_seen=items_seen, base_url=base_url)
            else:
                return {"iid_ref": self.get_docid(node)}

        elif node.tag == "meta":
            return node.get("content", "")

        elif node.tag in ("audio", "embed", "iframe", "img", "source", "track", "video"):
            return urljoin(base_url, strip_html5_whitespace(node.get("src", "")))

        elif node.tag in ("a", "area", "link"):
            return urljoin(base_url, strip_html5_whitespace(node.get("href", "")))

        elif node.tag in ("object",):
            return urljoin(base_url, strip_html5_whitespace(node.get("data", "")))

        elif node.tag in ("data", "meter"):
            return node.get("value", "")

        elif node.tag in ("time",):
            return node.get("datetime", "")

        # not in W3C specs but used in schema.org examples
        elif node.get("content"):
            return node.get("content")

        else:
            return self._extract_textContent(node)

    def _extract_textContent(self, node):
        return html_text.etree_to_text(node)


MicrodataExtractor = LxmlMicrodataExtractor
