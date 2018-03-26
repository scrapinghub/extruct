import logging
import argparse
from lxml.html import fromstring
from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.opengraph import OpenGraphExtractor
from extruct.microformat import MicroformatExtractor
from extruct.xmldom import XmlDomHTMLParser


logger = logging.getLogger(__name__)


def extract(args=None):
    parser = argparse.ArgumentParser()
    arg = parser.add_argument
    arg('htmlstring', help='string with valid html document')
    arg('--url', default ='http://www.example.com/',
        help='url to the html document')
    arg('--encoding', default='UTF-8', help='encoding of the html document')
    arg('--syntaxes', default='all', help='Either list of microdata syntaxes to\
          use or "all" (syntaxes available [microdata, microformat, rdfa, \
          opengraph, jsonld])')
    arg('--errors', default='strict', choices=['log', 'ignore', 'strict'],
        help='possible values: log, save exceptions to extruct.log, ignore, \
              ignore exceptions or strict (default), raise exceptions')
    args = parser.parse_args(args)
    domparser = XmlDomHTMLParser(encoding=args.encoding)
    tree = fromstring(args.htmlstring, parser=domparser)
    if args.syntaxes == 'all':
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
            output[label] = [obj for obj in extract(document=tree,
                                                    url=args.url,
                                                    html=args.htmlstring)]
        except Exception:
            if args.errors == 'log':
                logger.exception("Failed to parse %s", args.url)
            if args.errors == 'ignore':
                pass
    return output
