import json
import unittest
from utils import jsonize_dict

try:
    import unittest.mock as mock
except ImportError:
    import mock
# from extruct.tool import metadata_from_url
from requests.exceptions import HTTPError
from tests import get_testdata

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


class TestTool(unittest.TestCase):

    def setUp(self):
        self.expected = json.loads(get_testdata('songkick', 'tovestyrke.json').decode('UTF-8'))
        self.url = 'https://www.songkick.com/concerts/30166884-tove-styrke-at-hoxton-square-bar-and-kitchen'

    @mock.patch('extruct.tool.requests.get')
    def test_metadata_from_url_all_types(self, mock_get):
        expected = self.expected
        expected['url'] = self.url
        expected['status'] = '200 OK'
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata('songkick', 'tovestyrke.html'),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url)
        self.assertEqual(jsonize_dict(data), expected)

    @mock.patch('extruct.tool.requests.get')
    def test_metadata_from_url_jsonld_only(self, mock_get):
        expected = {
            'json-ld': self.expected['json-ld'],
            'url': self.url,
            'status': '200 OK',
        }
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata('songkick', 'tovestyrke.html'),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url, microdata=False, rdfa=False,
                                 opengraph=False, microformat=False)
        self.assertEqual(jsonize_dict(data), expected)


    @mock.patch('extruct.tool.requests.get')
    def test_metadata_from_url_microdata_only(self, mock_get):
        expected = {
            'microdata': self.expected['microdata'],
            'url': self.url,
            'status': '200 OK',
        }
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata('songkick', 'tovestyrke.html'),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url, jsonld=False, rdfa=False,
                                 opengraph=False, microformat=False)

        self.assertEqual(jsonize_dict(data), expected)

    @mock.patch('extruct.tool.requests.get')
    def test_metadata_from_url_rdfa_only(self, mock_get):
        expected = {
            'rdfa': self.expected['rdfa'],
            'url': self.url,
            'status': '200 OK',
        }
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata('songkick', 'tovestyrke.html'),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url, microdata=False, jsonld=False,
                                 opengraph=False, microformat=False)
        self.assertEqual(jsonize_dict(data), expected)

    @mock.patch('extruct.tool.requests.get')
    def test_metadata_from_url_unauthorized_page(self, mock_get):
        url = 'http://example.com/unauthorized'
        expected = {
            'url': url,
            'status': '401 Unauthorized',
        }
        mock_response = build_mock_response(
            url,
            reason='Unauthorized',
            status=401,
        )
        mock_get.return_value = mock_response
        mock_response.raise_for_status.side_effect = http_error

        data = metadata_from_url(url)
        self.assertEqual(data, expected)


def build_mock_response(url, encoding='utf-8', content='', reason='OK', status=200):
    mock_response = mock.Mock()
    mock_response.url = url
    mock_response.encoding = encoding
    mock_response.content = content
    mock_response.reason = reason
    mock_response.status_code = status
    return mock_response


def http_error():
    raise HTTPError()

if __name__ == '__main__':
    unittest.main()
