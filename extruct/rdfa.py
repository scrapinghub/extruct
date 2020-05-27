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

_OG_NAMESPACES = {
  'og': 'http://ogp.me/ns#',
  'music': 'http://ogp.me/ns/music#',
  'video': 'http://ogp.me/ns/video#',
  'article': 'http://ogp.me/ns/article#',
  'book': 'http://ogp.me/ns/book#',
  'profile': 'http://ogp.me/ns/profile#'
}

_OG_NAMESPACES_TAGS = {
  'og': 'xmlns:og',
  'music': 'xmlns:music',
  'video': 'xmlns:video',
  'article': 'xmlns:article',
  'book': 'xmlns:book',
  'profile': 'xmlns:profile'
}


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
        document = self.expandedOGSupport(document)
        g = PyRdfa(options, base=base_url).graph_from_DOM(document, graph=Graph(), pgraph=Graph())
        jsonld_string = g.serialize(format='json-ld', auto_compact=not expanded).decode('utf-8')
        return json.loads(jsonld_string)

    def expandedOGSupport(self,document):
      prefixDic = {}
      for head in document.xpath('//head'):
        for el in head.xpath('meta[@property and @content]'):
          prop = el.attrib['property']
          ns = prop.partition(':')[0]
          if ns in _OG_NAMESPACES.keys():
            prefixDic[_OG_NAMESPACES_TAGS[ns]] = _OG_NAMESPACES[ns]

      html_element = None
      for element in document.iter():
        if element.tag == 'html':
          html_element = element
          break

      if html_element is not None:
        for k in prefixDic.keys():
          if not (html_element.get(k)):
            html_element.set(k,prefixDic[k])
      return document