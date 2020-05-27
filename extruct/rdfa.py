# -*- coding: utf-8 -*-
"""
RDFa extractor

Based on pyrdfa3 and rdflib
"""
import json
import logging
import re

rdflib_logger = logging.getLogger('rdflib')
rdflib_logger.setLevel(logging.ERROR)

from rdflib import Graph, logger as rdflib_logger
from rdflib.plugins.parsers.pyRdfa import pyRdfa as PyRdfa, Options, logger as pyrdfa_logger
from rdflib.plugins.parsers.pyRdfa.initialcontext import initial_context

from extruct.utils import parse_xmldom_html


# silence rdflib/PyRdfa INFO logs
rdflib_logger.setLevel(logging.ERROR)
pyrdfa_logger.setLevel(logging.ERROR)

initial_context["http://www.w3.org/2011/rdfa-context/rdfa-1.1"].ns.update({
    "twitter": "https://dev.twitter.com/cards#",
    "fb": "http://ogp.me/ns/fb#"
})


class RDFaExtractor(object):
    
    # expands namespace to match with returned json (ex: og -> 'http://ogp.me/ns#')
    def replaceNS(self, prop, html_element, head_element):
        
        # context namespaces taken from pyrdfa3
        # https://github.com/RDFLib/PyRDFa/blob/master/pyRdfa/initialcontext.py
        context = {
            'owl'   : 'http://www.w3.org/2002/07/owl#',
            'gr'    : 'http://purl.org/goodrelations/v1#',
            'ctag'    : 'http://commontag.org/ns#',
            'cc'    : 'http://creativecommons.org/ns#',
            'grddl'   : 'http://www.w3.org/2003/g/data-view#',
            'rif'   : 'http://www.w3.org/2007/rif#',
            'sioc'    : 'http://rdfs.org/sioc/ns#',
            'skos'    : 'http://www.w3.org/2004/02/skos/core#',
            'xml'   : 'http://www.w3.org/XML/1998/namespace',
            'rdfs'    : 'http://www.w3.org/2000/01/rdf-schema#',
            'rev'   : 'http://purl.org/stuff/rev#',
            'rdfa'    : 'http://www.w3.org/ns/rdfa#',
            'dc'    : 'http://purl.org/dc/terms/',
            'foaf'    : 'http://xmlns.com/foaf/0.1/',
            'void'    : 'http://rdfs.org/ns/void#',
            'ical'    : 'http://www.w3.org/2002/12/cal/icaltzd#',
            'vcard'   : 'http://www.w3.org/2006/vcard/ns#',
            'wdrs'    : 'http://www.w3.org/2007/05/powder-s#',
            'og'    : 'http://ogp.me/ns#',
            'wdr'   : 'http://www.w3.org/2007/05/powder#',
            'rdf'   : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'xhv'   : 'http://www.w3.org/1999/xhtml/vocab#',
            'xsd'   : 'http://www.w3.org/2001/XMLSchema#',
            'v'     : 'http://rdf.data-vocabulary.org/#',
            'skosxl'  : 'http://www.w3.org/2008/05/skos-xl#',
            'schema'  : 'http://schema.org/',
        }

        if 'http://' in prop:
            return prop

        prefix = prop.split(':')[0]
        
        match = None
        if head_element.get('prefix'):
            match = re.search(prefix + ': [^\s]+', head_element.get('prefix'))

        # if namespace taken from prefix attribute in head tag
        if match:
            ns = match.group().split(': ')[1]
            return ns + prop.split(':')[1]

        # if namespace taken from xmlns attribute in html tag
        if ('xmlns:' + prefix) in html_element.keys():
            return html_element.get('xmlns:' + prefix) + prop.split(':')[1]

        # if namespace present in inital context
        if prefix in context:
            return context[prefix] + prop.split(':')[1]

        return prop
    
    # sorts the rdfa tags in jsonld string
    def sort(self, json_object, ordered, key):
        for i in range(len(ordered)):
            if json_object[key][i]['@value'] != ordered[i]:
                for j in range(i, len(json_object[key])):
                    if json_object[key][j]['@value'] == ordered[i]:
                        t = json_object[key][j]
                        json_object[key][j] = json_object[key][i]
                        json_object[key][i] = t
                        continue
    
    
    # fixes order of rdfa tags in jsonld string
    # by comparing with order in document object
    def fixOrder(self, jsonld_string, document):
        try:
            html_element = document.xpath('/html')[0]
            head_element = document.xpath('//head')[0]
        except IndexError:
            return json.loads(jsonld_string)
                
        for meta_tag in head_element.xpath("meta[@property]"):
            meta_tag.attrib['property'] = self.replaceNS(meta_tag.attrib['property'], html_element, head_element)
            
        json_objects = json.loads(jsonld_string)

        for json_object in json_objects:
            keys = json_object.keys()

            ordered = []
            
            for key in keys:
                if type(json_object[key]) is list and len(json_object[key]) > 1:
                    ordered = list(map(lambda meta_tag: meta_tag.get('content'), head_element.xpath("meta[@property='" + key + "']")))

                    self.sort(json_object, ordered, key)
                    ordered.clear()

        return json_objects

    def extract(self, htmlstring, base_url=None, encoding="UTF-8",
                expanded=True):
        tree = parse_xmldom_html(htmlstring, encoding=encoding)
        return self.extract_items(tree, base_url=base_url, expanded=expanded)

    def extract_items(self, document, base_url=None, expanded=True):
        options = Options(output_processor_graph=True,
                          embedded_rdf=False,
                          space_preserve=True,
                          vocab_expansion=False,
                          vocab_cache=False,
                          vocab_cache_report=False,
                          refresh_vocab_cache=False,
                          check_lite=False)

        g = PyRdfa(options, base=base_url).graph_from_DOM(document, graph=Graph(), pgraph=Graph())
        jsonld_string = g.serialize(format='json-ld', auto_compact=not expanded).decode('utf-8')
        
        return self.fixOrder(jsonld_string, document)
