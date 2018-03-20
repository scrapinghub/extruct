import argparse
import json

import lxml
import requests
from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.opengraph import OpenGraphExtractor
from extruct.microformat import MicroformatExtractor
from extruct.xmldom import XmlDomHTMLParser


def metadata_from_url(url, microdata=True, jsonld=True, rdfa=True,
                      microformat=True, opengraph=True):
    resp = requests.get(url, timeout=30)
    result = {'url': url, 'status': '{} {}'.format(resp.status_code, resp.reason)}
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        return result

    parser = XmlDomHTMLParser(encoding=resp.encoding)
    tree = lxml.html.fromstring(resp.content, parser=parser)

    if microdata:
        mde = MicrodataExtractor(nested=True)
        result['microdata'] = mde.extract_items(tree, resp.url)

    if jsonld:
        jsonlde = JsonLdExtractor()
        result['json-ld'] = jsonlde.extract_items(tree, resp.url)

    if rdfa:
        rdfae = RDFaExtractor()
        result['rdfa'] = rdfae.extract_items(tree, resp.url)

    if opengraph:
        oge = OpenGraphExtractor()
        result['opengraph'] = [obj for obj in oge.extract_items(tree, resp.url)]

    if microformat:
        mfmate = MicroformatExtractor()
        result['microformat'] = [obj for obj in mfmate.extract_items(html=resp.content, url=resp.url)]

    return result


def main():
    parser = argparse.ArgumentParser(prog='extruct', description=__doc__)
    parser.add_argument('url', help='The target URL')
    parser.add_argument(
        '--microdata',
        action='store_true',
        default=False,
        help='Extract W3C Microdata from the page.',
    )
    parser.add_argument(
        '--jsonld',
        action='store_true',
        default=False,
        help='Extract JSON-LD metadata from the page.',
    )
    parser.add_argument(
        '--rdfa',
        action='store_true',
        default=False,
        help='Extract RDFa metadata from the page.',
    )
    parser.add_argument(
        '--microformat',
        action='store_true',
        default=False,
        help='Extract microformat metadata from the page.',
    )
    parser.add_argument(
        '--opengraph',
        action='store_true',
        default=False,
        help='Extract opengraph metadata from the page.',
    )
    args = parser.parse_args()

    if any((args.microdata, args.jsonld, args.rdfa, args.microformat, args.opengraph)):
        metadata = metadata_from_url(args.url, args.microdata, args.jsonld,
                                     args.rdfa, args.microformat, args.opengraph)
    else:
        metadata = metadata_from_url(args.url)
    return json.dumps(metadata, indent=2, sort_keys=True)
