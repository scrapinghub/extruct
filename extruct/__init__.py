import logging
from lxml.html import fromstring
from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.opengraph import OpenGraphExtractor
from extruct.microformat import MicroformatExtractor
from extruct.xmldom import XmlDomHTMLParser


logger = logging.getLogger(__name__)


def extract(htmlstring, url='http://www.example.com/', encoding="UTF-8",
            syntaxes="all", schema_context='http://schema.org'):
    domparser = XmlDomHTMLParser(encoding=encoding)
    tree = fromstring(htmlstring, parser=domparser)
    if syntaxes == 'all':
        syntaxes = ['microdata', 'jsonld', 'opengraph', 'microformat', 'rdfa']
    processors = []
    if 'microdata' in syntaxes:
        processors.append(('microdata', MicrodataExtractor().extract_items))
    if 'jsonld' in syntaxes:
        processors.append(('jsonld', JsonLdExtractor().extract_items))
    if 'opengraph' in syntaxes:
        processors.append(('opengraph', OpenGraphExtractor().extract_items))
    if 'microformat' in syntaxes:
        processors.append(('microformat', MicroformatExtractor().extract_items))
    if 'rdfa' in syntaxes:
        processors.append(('rdfa', RDFaExtractor().extract_items))

    output = {}
    for label, extract in processors:
        try:
            output[label] = [obj for obj in extract(document=tree, url=url, html=htmlstring)]
        except Exception:
            logger.exception("Failed to parse %s", url)
    return output
