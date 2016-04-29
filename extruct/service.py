import requests
import json

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
from gevent import monkey

# gevent monkey patching
monkey.patch_all()

from bottle import route, run, request, response

import lxml.html
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.jsonld import JsonLdExtractor


def JSON(func):
    def _decorated(*args, **kwargs):
        for e in func(*args, **kwargs):
            yield json.dumps(e)
    return _decorated


def async_extruct(url, microdata=True, jsonld=True):
    response.content_type = 'application/json'
    resp = requests.get(url, timeout=30)

    parser = lxml.html.HTMLParser(encoding=resp.encoding)
    lxmldoc = lxml.html.fromstring(resp.content, parser=parser)

    result = {'url': url, 'status': 'ok'}

    if microdata:
        mde = MicrodataExtractor(nested=True)
        microdata = mde.extract_items(lxmldoc, url)
        if microdata.get('items', []):
            result['microdata'] = microdata

    if jsonld:
        jsonlde = JsonLdExtractor()
        jsonldata = jsonlde.extract_items(lxmldoc)
        if jsonldata.get('items', []):
            result['json-ld'] = jsonldata

    return result


@route('/')
def extruct_root():
    return """
    <html>
      <head><title>Extruct Service</title></head>
      <body>
       <h1>Extruct Service</h1>
       <p>
        <h3>Supported methods</h3>

        <pre>
        /extruct/<URL>
        method = GET


        /extruct/batch
        method = POST
        params:
            urls - a list of URLs separted by newlines
            urlsfile - a file with one URL per line
        </pre>
       </p>
      </body>
    </html>
    """

@route('/extruct/<url:re:.*?>')
@JSON
def extruct(url=None):
    if not url:
        yield {'message': 'No url provided'}
        return
    try:
        yield async_extruct(url)
    except Exception as e:
        yield {'url': url, 'status': 'error', 'message': repr(e)}

@route('/extruct/batch', method='POST')
def extruct_batch():
    urlsparam = request.params.get('urls')
    try:
        flobj = BytesIO(urlsparam) if urlsparam else request.files.get('urlsfile').file
    except AttributeError:
        yield json.dumps({'message': 'No url provided'})
        return
    if not flobj:
        yield json.dumps({'message': 'No url provided'})
        return
    # assume the file content one URL per file
    for url in flobj:
        if url.startswith(('http://', 'https://')):
            yield "%s\n" % json.dumps(async_extruct(url))


if __name__ ==  '__main__':
    run(host='0.0.0.0', port=10005, server='gevent')
