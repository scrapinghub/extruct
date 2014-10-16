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

    def __init__(self, nested=True):
        self.nested = nested

    def get_docid(self, node):
        return int(self._xp_item_docid(node))

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
        itemid = self.get_docid(node)

        if self.nested:
            if itemid in self.items_seen:
                return
            self.items_seen.add(itemid)

        item = {}
        if not self.nested:
            item["iid"] = itemid
        types = node.get('itemtype', '').split()
        if types:
            item["type"] = types

            itemid = node.get('itemid')
            if itemid:
                item["id"] = itemid.strip()

        properties = collections.defaultdict(list)
        for name, value in self.extract_properties(node):
            properties[name].append(value)

        props = []
        for (name, values) in properties.items():
            if len(values) == 1:
                props.append((name, values[0]))
            else:
                props.append((name, values))

        item["properties"] = dict(props)

        # not in the specs, but can be handy
        #textContent = self.extract_textContent(node)
        #if textContent:
            #item["textContent"] = textContent

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
            if self.nested:
                return self.extract_item(node)
            else:
                return {"iid_ref": self.get_docid(node)}

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

        # not in W3C specs but used in schema.org examples
        elif node.tag in ("meta",) and node.get("content"):
            return node.get("content")

        else:
            return self.extract_textContent(node)

    def extract_textContent(self, node):
        return lxml.html.tostring(node, method="text", encoding=unicode,
                    with_tail=False).strip()
