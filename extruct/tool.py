import argparse
import json

import requests
from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor


def metadata_from_url(url, microdata=True, jsonld=True, rdfa=True):
    resp = requests.get(url, timeout=30)
    result = {'url': url, 'status': '{} {}'.format(resp.status_code, resp.reason)}
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        return result

    if microdata:
        mde = MicrodataExtractor(nested=True)
        result['microdata'] = mde.extract(resp.content, resp.url, resp.encoding)

    if jsonld:
        jsonlde = JsonLdExtractor()
        result['json-ld'] = jsonlde.extract(resp.content, resp.url, resp.encoding)

    if rdfa:
        rdfae = RDFaExtractor()
        result['rdfa'] = rdfae.extract(resp.content, resp.url, resp.encoding)

    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
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
    args = parser.parse_args()

    if any((args.microdata, args.jsonld, args.rdfa)):
        metadata = metadata_from_url(args.url, args.microdata, args.jsonld, args.rdfa)
    else:
        metadata = metadata_from_url(args.url)
    return json.dumps(metadata, indent=2, sort_keys=True)
