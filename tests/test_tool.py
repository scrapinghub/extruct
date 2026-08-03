# mypy: disallow_untyped_defs=False
import json
import unittest
import unittest.mock as mock

from requests.exceptions import HTTPError

from extruct.tool import main, metadata_from_url
from tests import get_testdata, jsonize_dict


class TestTool(unittest.TestCase):
    def setUp(self):
        self.expected = json.loads(
            get_testdata("songkick", "tovestyrke.json").decode("UTF-8")
        )
        self.url = "https://www.songkick.com/concerts/30166884-tove-styrke-at-hoxton-square-bar-and-kitchen"

    @mock.patch("extruct.tool.requests.get")
    def test_metadata_from_url_all_types(self, mock_get):
        expected = self.expected
        expected["url"] = self.url
        expected["status"] = "200 OK"
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata("songkick", "tovestyrke.html"),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url)
        self.assertEqual(jsonize_dict(data), expected)

    @mock.patch("extruct.tool.requests.get")
    def test_metadata_from_url_jsonld_only(self, mock_get):
        expected = {
            "json-ld": self.expected["json-ld"],
            "url": self.url,
            "status": "200 OK",
        }
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata("songkick", "tovestyrke.html"),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url, syntaxes=["json-ld"])
        self.assertEqual(jsonize_dict(data), expected)

    @mock.patch("extruct.tool.requests.get")
    def test_metadata_from_url_microdata_only(self, mock_get):
        expected = {
            "microdata": self.expected["microdata"],
            "url": self.url,
            "status": "200 OK",
        }
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata("songkick", "tovestyrke.html"),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url, syntaxes=["microdata"])

        self.assertEqual(jsonize_dict(data), expected)

    @mock.patch("extruct.tool.requests.get")
    def test_metadata_from_url_rdfa_only(self, mock_get):
        expected = {
            "rdfa": self.expected["rdfa"],
            "url": self.url,
            "status": "200 OK",
        }
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata("songkick", "tovestyrke.html"),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url, syntaxes=["rdfa"])
        self.assertEqual(jsonize_dict(data), expected)

    @mock.patch("extruct.tool.requests.get")
    def test_metadata_from_url_opengraph_only(self, mock_get):
        expected = {
            "opengraph": self.expected["opengraph"],
            "url": self.url,
            "status": "200 OK",
        }
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata("songkick", "tovestyrke.html"),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url, syntaxes=["opengraph"])
        self.assertEqual(jsonize_dict(data), expected)

    @mock.patch("extruct.tool.requests.get")
    def test_metadata_from_url_microformat_only(self, mock_get):
        expected = {
            "microformat": self.expected["microformat"],
            "url": self.url,
            "status": "200 OK",
        }
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata("songkick", "tovestyrke.html"),
        )
        mock_get.return_value = mock_response

        data = metadata_from_url(self.url, syntaxes=["microformat"])
        self.assertEqual(jsonize_dict(data), expected)

    @mock.patch("extruct.tool.requests.get")
    def test_metadata_from_url_unauthorized_page(self, mock_get):
        url = "http://example.com/unauthorized"
        expected = {
            "url": url,
            "status": "401 Unauthorized",
        }
        mock_response = build_mock_response(
            url,
            reason="Unauthorized",
            status=401,
        )
        mock_get.return_value = mock_response
        mock_response.raise_for_status.side_effect = http_error

        data = metadata_from_url(url)
        self.assertEqual(data, expected)

    @mock.patch("extruct.tool.requests.get")
    def test_main_all(self, mock_get):
        expected = self.expected
        expected["url"] = self.url
        expected["status"] = "200 OK"
        expected = json.dumps(expected, indent=2, sort_keys=True)
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata("songkick", "tovestyrke.html"),
        )
        mock_get.return_value = mock_response

        data = main([self.url])
        self.assertEqual(data, expected)

    @mock.patch("extruct.tool.requests.get")
    def test_main_single_syntax(self, mock_get):
        data = {
            "opengraph": self.expected["opengraph"],
            "url": self.url,
            "status": "200 OK",
        }
        expected = json.dumps(data, indent=2, sort_keys=True)
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata("songkick", "tovestyrke.html"),
        )
        mock_get.return_value = mock_response

        data = main([self.url, "--syntax", "opengraph"])
        self.assertEqual(data, expected)

    @mock.patch("extruct.tool.requests.get")
    def test_main_multiple_syntaxes(self, mock_get):
        data = {
            "opengraph": self.expected["opengraph"],
            "microdata": self.expected["microdata"],
            "url": self.url,
            "status": "200 OK",
        }
        expected = json.dumps(data, indent=2, sort_keys=True)
        mock_response = build_mock_response(
            url=self.url,
            content=get_testdata("songkick", "tovestyrke.html"),
        )
        mock_get.return_value = mock_response

        data = main([self.url, "--syntax", "opengraph", "microdata"])
        self.assertEqual(data, expected)


def build_mock_response(url, encoding="utf-8", content="", reason="OK", status=200):
    mock_response = mock.Mock()
    mock_response.url = url
    mock_response.encoding = encoding
    mock_response.content = content
    mock_response.reason = reason
    mock_response.status_code = status
    return mock_response


def http_error():
    raise HTTPError()
