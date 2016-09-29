# -*- coding: utf-8 -*-
"""
RDFa extractor

Based on pyrdfa3 and rdflib
"""
import json
from xml.dom import Node
from xml.dom.minidom import Attr, NamedNodeMap

from lxml.etree import ElementBase, _ElementStringResult, _ElementUnicodeResult
from lxml.html import fromstring, HTMLParser, HtmlElementClassLookup

from rdflib import Graph
from rdflib.plugins.parsers.structureddata import RDFaParser
from rdflib.plugin import register, Parser

from rdflibxml import PyRdfa, Options

# load the JSON-LD serializer
register('json-ld', Parser, 'rdflib_jsonld.parser', 'JsonLDParser')


class DomElementUnicodeResult(object):
    def __init__(self, text):
        self.text = text

    @property
    def nodeType(self):
        return Node.TEXT_NODE

    @property
    def data(self):
        if isinstance(self.text, _ElementUnicodeResult):
            return self.text
        else:
            raise RuntimeError


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

    @property
    def documentElement(self):
        return self.getroottree().getroot()

    @property
    def nodeType(self):
        return lxmlDomNodeType(self)

    @property
    def nodeName(self):
        # FIXME: this is a simpification
        return self.tag

    @property
    def tagName(self):
        return self.tag

    def hasAttribute(self, name):
        return name in self.attrib

    def getAttribute(self, name):
        return self.get(name)

    def setAttribute(self, name, value):
        self.set(name, value)

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
    def childNodes(self):
        for n in self.xpath('child::node()'):
            nt = lxmlDomNodeType(n)
            if nt == Node.TEXT_NODE:
                # somehow one cannot set attributes on _ElementUnicodeResult instance
                # so we build an object out of it
                if isinstance(n, _ElementUnicodeResult):
                    n = DomElementUnicodeResult(n)
                else:
                    n.nodeType = nt
                    n.data = n
            yield n

    def getElementsByTagName(self, name):
        #print("getElementsByTagName(%r)" % (name,))
        return self.iterdescendants(name)

    def getElementById(self, i):
        #print("getElementById(%r)" % (i, self.get_element_by_id(i)))
        return self.get_element_by_id(i)

    @property
    def data(self):
        print("data(%r)" % self)
        if isinstance(self, (_ElementStringResult, _ElementUnicodeResult)):
            return self
        else:
            raise RuntimeError


class DomHtmlElementClassLookup(HtmlElementClassLookup):
    def lookup(self, node_type, document, namespace, name):
        cur = super(DomHtmlElementClassLookup, self).lookup(node_type, document, namespace, name)
        return type('Dom'+cur.__name__, (cur, DomHtmlMixin), {})


class XmlDomHTMLParser(HTMLParser):
    """An HTML parser that is configured to return XmlDomHtmlElement
    objects, compatible with xml.dom API
    """
    def __init__(self, **kwargs):
        super(HTMLParser, self).__init__(**kwargs)
        parser_lookup = DomHtmlElementClassLookup()
        self.set_element_class_lookup(parser_lookup)


class LxmlRDFaParser(RDFaParser):
    def _process(self, graph, pgraph, baseURI, orig_source,
                 media_type="",
                 rdfa_version=None,
                 embedded_rdf=False,
                 space_preserve=True,
                 vocab_expansion=False,
                 vocab_cache=False,
                 vocab_cache_report=False,
                 refresh_vocab_cache=False,
                 check_lite=False):

        processor_graph = pgraph if pgraph is not None else Graph()
        self.options = Options(output_processor_graph=True,
                               embedded_rdf=embedded_rdf,
                               space_preserve=space_preserve,
                               vocab_expansion=vocab_expansion,
                               vocab_cache=vocab_cache,
                               vocab_cache_report=vocab_cache_report,
                               refresh_vocab_cache=refresh_vocab_cache,
                               check_lite=check_lite)

        if media_type is None:
            media_type = ""

        processor = PyRdfa(self.options,
                           base=baseURI,
                           media_type=media_type,
                           rdfa_version=rdfa_version)
        domparser = XmlDomHTMLParser()
        tree = fromstring(orig_source.getvalue().encode('utf-8'), parser=domparser)
        processor.graph_from_DOM(tree, graph=graph, pgraph=processor_graph)


class RDFaExtractor(object):

    def extract(self, htmlstring, url='http://www.example.com/', encoding="UTF-8"):
        g = Graph()
        g.parse(data=htmlstring, format='rdfa-lxml')
        jsonld_string = g.serialize(format='json-ld')
        return {"items": json.loads(jsonld_string)}


register('rdfa-lxml', Parser, 'extruct.rdfa', 'LxmlRDFaParser')
