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

    def test_opengraph_outside_head(self):
        body = b"""<html prefix="a: http://a.example/"><head prefix="b: http://b.example/">
            <meta property="og:title" content="Title">
            </head><body>
            <meta property="og:type" content="website">
            <meta property="b:x" content="1">
            <meta property="c:y" content="2">
            </body></html>"""
        data = OpenGraphExtractor().extract(body)
        self.assertEqual(
            data,
            [
                {
                    "namespace": {
                        "a": "http://a.example/",
                        "b": "http://b.example/",
                        "og": "http://ogp.me/ns#",
                    },
                    "properties": [
                        ("og:title", "Title"),
                        ("og:type", "website"),
                        ("b:x", "1"),
                    ],
                }
            ],
        )

    def test_opengraph_no_head(self):
        body = b'<p>x</p><meta property="og:title" content="Title">'
        data = OpenGraphExtractor().extract(body)
        self.assertEqual(
            data,
            [
                {
                    "namespace": {"og": "http://ogp.me/ns#"},
                    "properties": [("og:title", "Title")],
                }
            ],
        )

    def test_opengraph_none(self):
        body = b'<head><meta property="c:y" content="2"></head>'
        self.assertEqual(OpenGraphExtractor().extract(body), [])
