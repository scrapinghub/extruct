# mypy: disallow_untyped_defs=False
# -*- coding: utf-8 -*-
import json
import unittest

import extruct
from extruct.utils import parse_html
from tests import get_testdata, jsonize_dict, replace_node_ref_with_node_id


class TestFlatten(unittest.TestCase):

    maxDiff = None

    def test_microdata(self):
        body = get_testdata("schema.org", "CreativeWork.001.html")
        tree = parse_html(body, encoding="UTF-8")
        expected = json.loads(
            get_testdata("schema.org", "CreativeWork_flat.001.json").decode("UTF-8")
        )
        data = extruct.extract(tree, uniform=True, syntaxes=["microdata"])
        self.assertEqual(jsonize_dict(data["microdata"]), expected["microdata"])

    def test_microdata_with_returning_node(self):
        body = get_testdata("schema.org", "CreativeWork.001.html")
        tree = parse_html(body, encoding="UTF-8")
        expected = json.loads(
            get_testdata(
                "schema.org", "CreativeWork_flat_with_node_id.001.json"
            ).decode("UTF-8")
        )
        data = extruct.extract(
            tree, uniform=True, return_html_node=True, syntaxes=["microdata"]
        )
        replace_node_ref_with_node_id(data["microdata"])
        self.assertEqual(jsonize_dict(data["microdata"]), expected["microdata"])

    def test_microformat(self):
        body = get_testdata("misc", "microformat_test.html")
        expected = json.loads(
            get_testdata("misc", "microformat_flat_test.json").decode("UTF-8")
        )
        data = extruct.extract(body, uniform=True, syntaxes=["microformat"])
        self.assertEqual(jsonize_dict(data["microformat"]), expected)

    def test_opengraph(self):
        body = get_testdata("misc", "opengraph_test.html")
        expected = json.loads(
            get_testdata("misc", "opengraph_flat_test.json").decode("UTF-8")
        )
        data = extruct.extract(body, uniform=True, syntaxes=["opengraph"])
        self.assertEqual(jsonize_dict(data["opengraph"]), expected)
