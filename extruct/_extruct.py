import logging
import warnings

from lxml.html import fromstring

from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.opengraph import OpenGraphExtractor
from extruct.microformat import MicroformatExtractor
from extruct.xmldom import XmlDomHTMLParser
from extruct.uniform import _umicrodata_microformat, _uopengraph


logger = logging.getLogger(__name__)
SYNTAXES = ['microdata', 'opengraph', 'json-ld', 'microformat', 'rdfa']


def extract(htmlstring, base_url=None, encoding="UTF-8",
            syntaxes=SYNTAXES,
            errors='strict',
            uniform=False,
            return_html_node=False,
            schema_context='http://schema.org',
            **kwargs):
    """htmlstring: string with valid html document;
       base_url: base url of the html document
       encoding: encoding of the html document
       syntaxes: list of syntaxes to extract, default SYNTAXES
       errors: set to 'log' to log the exceptions, 'ignore' to ignore them
               or 'strict'(default) to raise them
       uniform: if True uniform output format of all syntaxes to a list of dicts.
                Returned dicts structure:
                {'@context': 'http://example.com',
                 '@type': 'example_type',
                 /* All other the properties in keys here */
                 }
       return_html_node: if True, it includes into the result a HTML node of
                         respective embedded metadata under 'htmlNode' key.
                         The feature is supported only by microdata syntax.
                         Each node is of `lxml.etree.Element` type.
       schema_context: schema's context for current page"""
    if base_url is None and 'url' in kwargs:
        warnings.warn('"url" argument is deprecated, please use "base_url"',
                      DeprecationWarning)
        base_url = kwargs.pop('url')
    if kwargs:
        raise TypeError('Unexpected keyword arguments')
    if not (isinstance(syntaxes, list) and all(v in SYNTAXES for v in syntaxes)):
        raise ValueError("syntaxes must be a list with any or all (default) of"
                         "these values: {}".format(SYNTAXES))
    if errors not in ['log', 'ignore', 'strict']:
        raise ValueError('Invalid error command, valid values are either "log"'
                         ', "ignore" or "strict"')
    domparser = XmlDomHTMLParser(encoding=encoding)
    tree = fromstring(htmlstring, parser=domparser)
    processors = []
    if 'microdata' in syntaxes:
        processors.append(('microdata', MicrodataExtractor(add_html_node=return_html_node).extract_items, tree))
    if 'json-ld' in syntaxes:
        processors.append(('json-ld', JsonLdExtractor().extract_items, tree))
    if 'opengraph' in syntaxes:
        processors.append(('opengraph', OpenGraphExtractor().extract_items, tree))
    if 'microformat' in syntaxes:
        processors.append(('microformat', MicroformatExtractor().extract_items, htmlstring))
    if 'rdfa' in syntaxes:
        processors.append(('rdfa', RDFaExtractor().extract_items, tree))
    output = {}
    for label, extract, document in processors:
        try:
            output[label] = list(extract(document, base_url=base_url))
        except Exception:
            if errors == 'log':
                logger.exception('Failed to extract {}'.format(label))
            if errors == 'ignore':
                pass
            if errors == 'strict':
                raise

    if uniform:
        if 'microdata' in syntaxes:
            output['microdata'] = _umicrodata_microformat(output['microdata'],
                                                          schema_context=schema_context)
        if 'microformat' in syntaxes:
            output['microformat'] = _umicrodata_microformat(output['microformat'],
                                                            schema_context='http://microformats.org/wiki/')
        if 'opengraph' in syntaxes:
            output['opengraph'] = _uopengraph(output['opengraph'])
    return output
