# mypy: disallow_untyped_defs=False
import json
import unittest

from extruct.microformat import MicroformatExtractor
from tests import get_testdata, jsonize_dict


class TestMicroformat(unittest.TestCase):

    maxDiff = None

    def test_microformat(self):
        body = get_testdata("misc", "microformat_test.html")
        expected = json.loads(
            get_testdata("misc", "microformat_test.json").decode("UTF-8")
        )

        opengraphe = MicroformatExtractor()
        data = opengraphe.extract(body)
        self.assertEqual(jsonize_dict(data), expected)
