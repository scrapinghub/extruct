# mypy: disallow_untyped_defs=False
import json

from extruct.microformat import MicroformatExtractor
from tests import get_testdata, jsonize_dict


class TestMicroformat:
    def test_microformat(self):
        body = get_testdata("misc", "microformat_test.html")
        expected = json.loads(
            get_testdata("misc", "microformat_test.json").decode("UTF-8")
        )

        microformat_extractor = MicroformatExtractor()
        data = microformat_extractor.extract(body)

        assert jsonize_dict(data) == expected
