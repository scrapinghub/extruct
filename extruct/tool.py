import argparse
import json
import requests

import extruct
from extruct import SYNTAXES


def metadata_from_url(url, syntaxes=SYNTAXES, uniform=False,
                      schema_context='http://schema.org', errors='strict'):
    resp = requests.get(url, timeout=30)
    result = {'url': url, 'status': '{} {}'.format(resp.status_code, resp.reason)}
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        return result
    result.update(extruct.extract(resp.content,
                                  base_url=url,  # FIXME: use base url
                                  syntaxes=syntaxes, 
                                  uniform=uniform,
                                  schema_context=schema_context,
                                  errors=errors))
    return result


def main(args=None):
    parser = argparse.ArgumentParser(prog='extruct', description=__doc__)
    arg = parser.add_argument
    arg('url', help='The target URL')
    arg('--syntaxes', nargs='+',
        choices=SYNTAXES,
        default=SYNTAXES,
        help='List of syntaxes to extract. Valid values any or all (default):'
             'microdata, opengraph, microformat json-ld, rdfa.'
             'Example: --syntaxes microdata opengraph json-ld')
    arg('--uniform', default=False, 
        help='''If True uniform output format of all syntaxes to a list of dicts.
                Returned dicts structure:
                {'@context': 'http://example.com', 
                 '@type': 'example_type',
                 /* All other the properties in keys here */
                 }''')
    arg('--schema_context', default='http://schema.org', 
        help="schema's context for current page")
    arg('--errors',
        default='log',
        choices=['strict', 'log', 'ignore'], 
        help="errors: set to 'log'(default) to log the exceptions, 'ignore' to ignore"
             " them or 'strict' to raise them")
    args = parser.parse_args(args)
    metadata = metadata_from_url(args.url, args.syntaxes, args.uniform, 
                                 args.schema_context, args.errors)
    return json.dumps(metadata, indent=2, sort_keys=True)
