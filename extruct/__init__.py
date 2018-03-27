import logging
from lxml.html import fromstring
from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.opengraph import OpenGraphExtractor
from extruct.microformat import MicroformatExtractor
from extruct.xmldom import XmlDomHTMLParser

logger = logging.getLogger(__name__)
VALID = ('microdata', 'opengraph', 'jsonld', 'microformat', 'rdfa')

def extract(htmlstring, url='http://www.example.com/', encoding="UTF-8",
            syntaxes=['microdata', 'opengraph', 'jsonld', 'microformat', 'rdfa'],
            errors='strict'):
    """htmlstring: string with valid html document;
       url: url of the html documents
       encoding: encoding of the html document
       syntaxes: list of syntaxes to extract, default ['microdata', 'opengraph',
                 'jsonld', 'microformat', 'rdfa']
       errors: set to 'log' to save exceptions to file, 'ignore' to ignore them
               and 'strict'(default) to raise them"""
    if not (isinstance(syntaxes, list) and all(v in VALID for v in syntaxes)):
        raise ValueError("syntaxes must be a list with any or all (default) of \
                          these values: ['microdata', 'opengraph', 'jsonld', \
                          'microformat', 'rdfa']")
    domparser = XmlDomHTMLParser(encoding=encoding)
    tree = fromstring(htmlstring, parser=domparser)
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
            output[label] = [obj for obj in extract(document=tree,
                                                    url=url,
                                                    html=htmlstring)]
        except Exception:
            if errors == 'log':
                logger.exception("Failed to parse %s", url)
            if errors == 'ignore':
                pass
    return output
