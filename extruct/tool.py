import argparse
import json
import requests
import extruct

def metadata_from_url(url, syntaxes='all'):
    resp = requests.get(url, timeout=30)
    result = {'url': url, 'status': '{} {}'.format(resp.status_code, resp.reason)}
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        return result
    result.update(extruct.extract(resp.content, url=url, syntaxes=syntaxes))
    return result


def main(args=None):
    parser = argparse.ArgumentParser(prog='extruct', description=__doc__)
    arg = parser.add_argument
    arg('url', help='The target URL')
    arg('--syntaxes',
        default='all',
        help='Either list of microdata syntaxes to use or "all" (syntaxes\
             available [microdata, microformat, rdfa, opengraph, jsonld])')
    args = parser.parse_args(args)
    metadata = metadata_from_url(args.url, args.syntaxes)
    return json.dumps(metadata, indent=2, sort_keys=True)
