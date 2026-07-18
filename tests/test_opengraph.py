# mypy: disallow_untyped_defs=False
import json

from extruct.opengraph import OpenGraphExtractor
from tests import get_testdata, jsonize_dict


class TestOpengraph:
    def _test_opengraph(self, name: str) -> None:
        body = get_testdata("misc", name + ".html")
        expected = json.loads(get_testdata("misc", name + ".json").decode("UTF-8"))

        opengraph = OpenGraphExtractor()
        data = opengraph.extract(body)
        assert jsonize_dict(data) == expected

    def test_opengraph(self):
        self._test_opengraph("opengraph_test")

    def test_opengraph_ns_product(self):
        self._test_opengraph("opengraph_ns_product_test")
