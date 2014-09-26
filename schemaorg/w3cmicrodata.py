"""
Microdata parser

Piece of code extracted form:
* http://blog.scrapinghub.com/2014/06/18/extracting-schema-org-microdata-using-scrapy-selectors-and-xpath/

Ported to lxml
follows http://www.w3.org/TR/microdata/#json

"""

import collections
import urlparse

import lxml.etree
import lxml.html


class MicrodataExtractor(object):
    _xp_item = lxml.etree.XPath('descendant-or-self::*[@itemscope]')
    _xp_prop = lxml.etree.XPath("""set:difference(.//*[@itemprop],
                                                  .//*[@itemscope]//*[@itemprop])""",
                                namespaces = {"set": "http://exslt.org/sets"})
    _xp_item_docid = lxml.etree.XPath("""count(preceding::*[@itemscope])
                                        + count(ancestor::*[@itemscope])
                                        + 1""")
    _xp_norm = lxml.etree.XPath('normalize-space(.)')



    def extract(self, htmlstring, url='http://www.example.com/', encoding="UTF-8"):
        self.url = url
        self.items_seen = set()
        parser = lxml.html.HTMLParser(encoding=encoding)
        lxmldoc = lxml.html.fromstring(htmlstring, parser=parser)
        return self.extract_items(lxmldoc)

    def extract_items(self, document):
        return {"items" : filter(bool, [self.extract_item(item)
                                        for item in self._xp_item(document)])}

    def extract_item(self, node):
        itemid = self._xp_item_docid(node)
        if itemid in self.items_seen:
            return
        self.items_seen.add(itemid)

        item = {}
        types = node.get('itemtype', '').split()
        if types:
            item["type"] = types

        properties = collections.defaultdict(list)
        for name, value in self.extract_properties(node):
            properties[name].append(value)

        item["properties"] = dict(properties.items())
        return item

    def extract_properties(self, node):
        for prop in self._xp_prop(node):
            for p, v in self.extract_property(prop):
                yield p, v

    def extract_property(self, node):
        props = node.get("itemprop").split()
        value = self.extract_property_value(node)
        return [(p, value) for p in props]

    def extract_property_value(self, node):
        #http://www.w3.org/TR/microdata/#values
        if node.get("itemscope") is not None:
            return self.extract_item(node)

        elif node.tag == "meta":
            return node.get("content", "")

        elif node.tag in ("audio", "embed", "iframe", "img", "source", "track", "video"):
            return urlparse.urljoin(self.url, node.get("src", ""))

        elif node.tag in ("a", "area", "link"):
            return urlparse.urljoin(self.url, node.get("href", ""))

        elif node.tag in ("object",):
            return node.get("data", "")

        elif node.tag in ("data", "meter"):
            return node.get("value", "")

        elif node.tag in ("time",):
            return node.get("datetime", "")

        elif node.get("content"):
            return node.get("content", "")

        else:
            return lxml.html.tostring(node, method="text", encoding=unicode,
                        with_tail=False).strip()
