# mypy: disallow_untyped_defs=False
import json
import unittest

import extruct
from extruct.utils import parse_html
from tests import get_testdata, jsonize_dict, replace_node_ref_with_node_id


class TestFlatten(unittest.TestCase):

    maxDiff = None

    def test_microdata(self):
        body, tree, expected = self._testdata_html_and_tree(
            "schema.org",
            "CreativeWork.001.html",
            "CreativeWork_flat.001.json",
        )
        syntax = "microdata"
        data = extruct.extract(body, uniform=True, syntaxes=[syntax])
        self.assertEqual(jsonize_dict(data[syntax]), expected[syntax])

        data = extruct.extract(tree, uniform=True, syntaxes=[syntax])
        self.assertEqual(jsonize_dict(data[syntax]), expected[syntax])

    def test_opengraph(self):
        body, tree, expected = self._testdata_html_and_tree(
            "misc",
            "opengraph_test.html",
            "opengraph_flat_test.json",
        )
        syntax = "opengraph"
        data = extruct.extract(body, uniform=True, syntaxes=[syntax])
        self.assertEqual(jsonize_dict(data[syntax]), expected)

        data = extruct.extract(tree, uniform=True, syntaxes=[syntax])
        self.assertEqual(jsonize_dict(data[syntax]), expected)

    def test_microdata_with_returning_node(self):
        body, tree, expected = self._testdata_html_and_tree(
            "schema.org",
            "CreativeWork.001.html",
            "CreativeWork_flat_with_node_id.001.json",
        )
        syntax = "microdata"
        data = extruct.extract(
            body, uniform=True, return_html_node=True, syntaxes=[syntax]
        )
        replace_node_ref_with_node_id(data[syntax])
        self.assertEqual(jsonize_dict(data[syntax]), expected[syntax])

        data = extruct.extract(
            tree, uniform=True, return_html_node=True, syntaxes=[syntax]
        )
        replace_node_ref_with_node_id(data[syntax])
        self.assertEqual(jsonize_dict(data[syntax]), expected[syntax])

    def test_microformat(self):
        body = get_testdata("misc", "microformat_test.html")
        expected = json.loads(
            get_testdata("misc", "microformat_flat_test.json").decode("UTF-8")
        )
        data = extruct.extract(body, uniform=True, syntaxes=["microformat"])
        self.assertEqual(jsonize_dict(data["microformat"]), expected)

    def _testdata_html_and_tree(self, root, path1, path2):
        body = get_testdata(root, path1)
        tree = parse_html(body, encoding="UTF-8")
        expected = json.loads(get_testdata(root, path2).decode("UTF-8"))
        return body, tree, expected
