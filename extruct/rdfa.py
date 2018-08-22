# -*- coding: utf-8 -*-
"""
RDFa extractor

Based on pyrdfa3 and rdflib
"""
import json
import logging

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
        return json.loads(jsonld_string)
