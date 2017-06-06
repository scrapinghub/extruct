from lxml.html import fromstring

from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.xmldom import XmlDomHTMLParser


def extract(htmlstring, url='http://www.example.com/', encoding="UTF-8"):
    domparser = XmlDomHTMLParser(encoding=encoding)
    tree = fromstring(htmlstring, parser=domparser)
    return {name: extractor.extract_items(tree, url=url)
            for name, extractor in (
                ('json-ld', JsonLdExtractor()),
                ('microdata', MicrodataExtractor()),
                ('rdfa', RDFaExtractor()))}
