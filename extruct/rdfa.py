# -*- coding: utf-8 -*-
"""
RDFa extractor

Based on pyrdfa3 and rdflib
"""
import json
import logging
from xml.dom import Node
from xml.dom.minidom import Attr, NamedNodeMap

from lxml.etree import ElementBase, _ElementStringResult, _ElementUnicodeResult, XPath, tostring
from lxml.html import fromstring, HTMLParser, HtmlElementClassLookup
from rdflib import Graph, logger as rdflib_logger
from rdflib.plugins.parsers.pyRdfa import pyRdfa as PyRdfa, Options, logger as pyrdfa_logger
from rdflib.plugins.parsers.pyRdfa.initialcontext import initial_context

from copy import deepcopy, copy

# silence rdflib/PyRdfa INFO logs
rdflib_logger.setLevel(logging.ERROR)
pyrdfa_logger.setLevel(logging.ERROR)

initial_context["http://www.w3.org/2011/rdfa-context/rdfa-1.1"].ns.update({
    "twitter": "https://dev.twitter.com/cards#",
    "fb": "http://ogp.me/ns/fb#"
})


class DomElementUnicodeResult(object):
    CDATA_SECTION_NODE = Node.CDATA_SECTION_NODE
    ELEMENT_NODE = Node.ELEMENT_NODE
    TEXT_NODE = Node.TEXT_NODE

    def __init__(self, text):
        self.text = text
        self.nodeType = Node.TEXT_NODE

    @property
    def data(self):
        if isinstance(self.text, _ElementUnicodeResult):
            return self.text
        else:
            raise RuntimeError


class DomTextNode(object):
    CDATA_SECTION_NODE = Node.CDATA_SECTION_NODE
    ELEMENT_NODE = Node.ELEMENT_NODE
    TEXT_NODE = Node.TEXT_NODE

    def __init__(self, text):
        self.data = text
        self.nodeType = Node.TEXT_NODE


def lxmlDomNodeType(node):
    if isinstance(node, ElementBase):
        return Node.ELEMENT_NODE

    elif isinstance(node, (_ElementStringResult, _ElementUnicodeResult)):
        if node.is_attribute:
            return Node.ATTRIBUTE_NODE
        else:
            return Node.TEXT_NODE
    else:
        return Node.NOTATION_NODE


class DomHtmlMixin(object):
    CDATA_SECTION_NODE = Node.CDATA_SECTION_NODE
    ELEMENT_NODE = Node.ELEMENT_NODE
    TEXT_NODE = Node.TEXT_NODE

    _xp_childrennodes = XPath('child::node()')

    @property
    def documentElement(self):
        return self.getroottree().getroot()

    @property
    def nodeType(self):
        return Node.ELEMENT_NODE

    @property
    def nodeName(self):
        # FIXME: this is a simpification
        return self.tag

    @property
    def tagName(self):
        return self.tag

    @property
    def localName(self):
        return self.xpath('local-name(.)')

    def hasAttribute(self, name):
        return name in self.attrib

    def getAttribute(self, name):
        return self.get(name)

    def setAttribute(self, name, value):
        self.set(name, value)

    def cloneNode(self, deep):
        return deepcopy(self) if deep else copy(self)

    @property
    def attributes(self):
        attrs = {}
        for name, value in self.attrib.items():
            a = Attr(name)
            a.value = value
            attrs[name] = a
        return NamedNodeMap(attrs, {}, self)

    @property
    def parentNode(self):
        return self.getparent()

    @property
    def childNodes_xpath(self):
        for n in self._xp_childrennodes(self):

            if isinstance(n, ElementBase):
                yield n

            elif isinstance(n, (_ElementStringResult, _ElementUnicodeResult)):

                if isinstance(n, _ElementUnicodeResult):
                    n = DomElementUnicodeResult(n)
                else:
                    n.nodeType = Node.TEXT_NODE
                    n.data = n
                yield n

    @property
    def childNodes(self):
        if self.text:
            yield DomTextNode(self.text)
        for n in self.iterchildren():
            yield n
            if n.tail:
                yield DomTextNode(n.tail)

    def getElementsByTagName(self, name):
        return self.iterdescendants(name)

    def getElementById(self, i):
        return self.get_element_by_id(i)

    @property
    def data(self):
        if isinstance(self, (_ElementStringResult, _ElementUnicodeResult)):
            return self
        else:
            raise RuntimeError

    def toxml(self, encoding=None):
        return tostring(self, encoding=encoding)



class DomHtmlElementClassLookup(HtmlElementClassLookup):
    _lookups = {}
    def lookup(self, node_type, document, namespace, name):
        k = (node_type, document, namespace, name)
        t = self._lookups.get(k)
        if t is None:
            cur = super(DomHtmlElementClassLookup, self).lookup(node_type, document, namespace, name)
            newtype = type('Dom'+cur.__name__, (cur, DomHtmlMixin), {})
            self._lookups[k] = newtype
            return newtype
        else:
            return t


class XmlDomHTMLParser(HTMLParser):
    """An HTML parser that is configured to return XmlDomHtmlElement
    objects, compatible with xml.dom API
    """
    def __init__(self, **kwargs):
        super(HTMLParser, self).__init__(**kwargs)
        parser_lookup = DomHtmlElementClassLookup()
        self.set_element_class_lookup(parser_lookup)


class RDFaExtractor(object):

    def extract(self, htmlstring, url='http://www.example.com/', encoding="UTF-8",
            expanded=True):

        domparser = XmlDomHTMLParser()
        tree = fromstring(htmlstring.encode('utf-8'), parser=domparser)
        return self.extract_items(tree, url, expanded=expanded)

    def extract_items(self, document, url, expanded=True):
        options = Options(output_processor_graph=True,
                          embedded_rdf=False,
                          space_preserve=True,
                          vocab_expansion=False,
                          vocab_cache=False,
                          vocab_cache_report=False,
                          refresh_vocab_cache=False,
                          check_lite=False)

        g = PyRdfa(options, base=url).graph_from_DOM(document, graph=Graph(), pgraph=Graph())
        jsonld_string = g.serialize(format='json-ld', auto_compact=not expanded).decode('utf-8')
        return json.loads(jsonld_string)
