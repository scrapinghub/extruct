import logging
from lxml.html import fromstring
from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.opengraph import OpenGraphExtractor
from extruct.microformat import MicroformatExtractor
from extruct.xmldom import XmlDomHTMLParser

logger = logging.getLogger(__name__)
SYNTAXES = ['microdata', 'opengraph', 'json-ld', 'microformat', 'rdfa']

def extract(htmlstring, url='http://www.example.com/', encoding="UTF-8",
            syntaxes=SYNTAXES,
            errors='strict'):
    """htmlstring: string with valid html document;
       url: url of the html documents
       encoding: encoding of the html document
       syntaxes: list of syntaxes to extract, default SYNTAXES
       errors: set to 'log' to save exceptions to file, 'ignore' to ignore them
               or 'strict'(default) to raise them"""
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
        processors.append(('microdata', MicrodataExtractor().extract_items))
    if 'json-ld' in syntaxes:
        processors.append(('json-ld', JsonLdExtractor().extract_items))
    if 'opengraph' in syntaxes:
        processors.append(('opengraph', OpenGraphExtractor().extract_items))
    if 'microformat' in syntaxes:
        processors.append(('microformat', MicroformatExtractor().extract_items))
    if 'rdfa' in syntaxes:
        processors.append(('rdfa', RDFaExtractor().extract_items))
    output = {}
    for label, extract in processors:
        try:
            output[label] = [obj for obj in extract(document=tree,
                                                    url=url,
                                                    html=htmlstring)]
        except Exception:
            if errors == 'log':
                logger.exception("Failed to extract {} from {}".format(label, url))
            if errors == 'ignore':
                pass
            if errors == 'strict':
                raise
    return output
