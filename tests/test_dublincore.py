# mypy: disallow_untyped_defs=False
import json

from extruct.dublincore import DublinCoreExtractor
from tests import get_testdata, jsonize_dict


class TestDublincore:
    def test_dublincore(self):
        body = get_testdata("misc", "dublincore_test.html")
        expected = json.loads(
            get_testdata("misc", "dublincore_test.json").decode("UTF-8")
        )

        dublincorext = DublinCoreExtractor()
        data = dublincorext.extract(body)

        assert jsonize_dict(data) == expected
