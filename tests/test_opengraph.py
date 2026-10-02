# mypy: disallow_untyped_defs=False
import json
import unittest

from extruct.opengraph import OpenGraphExtractor
from tests import get_testdata, jsonize_dict


class TestOpengraph(unittest.TestCase):

    maxDiff = None

    def _test_opengraph(self, name):
        body = get_testdata("misc", name + ".html")
        expected = json.loads(get_testdata("misc", name + ".json").decode("UTF-8"))

        opengraphe = OpenGraphExtractor()
        data = opengraphe.extract(body)
        self.assertEqual(jsonize_dict(data), expected)

    def test_opengraph(self):
        self._test_opengraph("opengraph_test")

    def test_opengraph_ns_product(self):
        self._test_opengraph("opengraph_ns_product_test")

    def test_opengraph_in_body(self):
        # OpenGraph tags are sometimes found in the body instead of (or
        # nested inside a wrapper element in) the head, e.g. when injected
        # dynamically by client-side code.
        self._test_opengraph("opengraph_body_test")

    def test_opengraph_in_head_and_body(self):
        self._test_opengraph("opengraph_head_and_body_test")

    def test_opengraph_no_head(self):
        body = b'<body><meta property="og:title" content="T"></body>'
        data = OpenGraphExtractor().extract(body)
        self.assertEqual(
            data,
            [
                {
                    "namespace": {"og": "http://ogp.me/ns#"},
                    "properties": [("og:title", "T")],
                }
            ],
        )
