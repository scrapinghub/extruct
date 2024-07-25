# mypy: disallow_untyped_defs=False
import json
import unittest

from extruct.w3cmicrodata import MicrodataExtractor
from tests import get_testdata


class TestMicrodata(unittest.TestCase):

    maxDiff = None

    def _test_schemaorg(self, schema, indexes=None):
        indexes = indexes or [1]
        for i in indexes:
            body = get_testdata("schema.org", f"{schema}.{i:03d}.html")
            expected = json.loads(
                get_testdata("schema.org", f"{schema}.{i:03d}.json").decode()
            )
            mde = MicrodataExtractor()
            data = mde.extract(body)
            self.assertEqual(data, expected)

    def test_schemaorg_CreativeWork(self):
        for i in [1]:
            body = get_testdata("schema.org", "CreativeWork.{:03d}.html".format(i))
            expected = json.loads(
                get_testdata("schema.org", "CreativeWork.{:03d}.json".format(i)).decode(
                    "UTF-8"
                )
            )

            mde = MicrodataExtractor()
            data = mde.extract(body)
            self.assertEqual(data, expected)

    def test_schemaorg_LocalBusiness(self):
        for i in [2, 3]:
            body = get_testdata("schema.org", "LocalBusiness.{:03d}.html".format(i))
            expected = json.loads(
                get_testdata(
                    "schema.org", "LocalBusiness.{:03d}.json".format(i)
                ).decode("UTF-8")
            )

            mde = MicrodataExtractor()
            data = mde.extract(body)
            self.assertEqual(data, expected)

    def test_schemaorg_MusicRecording(self):
        for i in [1]:
            body = get_testdata("schema.org", "MusicRecording.{:03d}.html".format(i))
            expected = json.loads(
                get_testdata(
                    "schema.org", "MusicRecording.{:03d}.json".format(i)
                ).decode("UTF-8")
            )

            mde = MicrodataExtractor()
            data = mde.extract(body)
            self.assertEqual(data, expected)

    def test_schemaorg_Event(self):
        for i in [1, 2, 3, 4, 8]:
            body = get_testdata("schema.org", "Event.{:03d}.html".format(i))
            expected = json.loads(
                get_testdata("schema.org", "Event.{:03d}.json".format(i)).decode(
                    "UTF-8"
                )
            )

            mde = MicrodataExtractor()
            data = mde.extract(body)

            self.assertEqual(data, expected)

    def test_schemaorg_SearchAction(self):
        self._test_schemaorg("SearchAction")

    def test_w3c_textContent_values(self):
        body = get_testdata("w3c", "microdata.4.2.strings.html")
        expected = json.loads(
            get_testdata("w3c", "microdata.4.2.strings.json").decode("UTF-8")
        )

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertEqual(data, expected)

    def test_w3c_textContent_values_unclean(self):
        body = get_testdata("w3c", "microdata.4.2.strings.unclean.html")
        expected = json.loads(
            get_testdata("w3c", "microdata.4.2.strings.unclean.json").decode("UTF-8")
        )

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertEqual(data, expected)

    def test_w3c_5_2(self):
        body = get_testdata("w3c", "microdata.5.2.html")
        expected = json.loads(get_testdata("w3c", "microdata.5.2.json").decode("UTF-8"))

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertEqual(data, expected)

    def test_w3c_5_3(self):
        body = get_testdata("w3c", "microdata.5.3.html")
        expected = json.loads(get_testdata("w3c", "microdata.5.3.json").decode("UTF-8"))

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertEqual(data, expected)

    def test_w3c_5_5(self):
        body = get_testdata("w3c", "microdata.5.5.html")
        expected = json.loads(get_testdata("w3c", "microdata.5.5.json").decode("UTF-8"))

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertEqual(data, expected)

    def test_w3c_7_1(self):
        body = get_testdata("w3c", "microdata.7.1.html")
        expected = json.loads(get_testdata("w3c", "microdata.7.1.json").decode("UTF-8"))

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body, "http://blog.example.com/progress-report")
        self.assertEqual(data, expected)

    def test_w3c_meter_element(self):
        body = get_testdata("w3c", "microdata.4.2.meter.html")
        expected = json.loads(
            get_testdata("w3c", "microdata.4.2.meter.json").decode("UTF-8")
        )

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertEqual(data, expected)

    def test_w3c_data_element(self):
        body = get_testdata("w3c", "microdata.4.2.data.html")
        expected = json.loads(
            get_testdata("w3c", "microdata.4.2.data.json").decode("UTF-8")
        )

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body)
        self.assertEqual(data, expected)

    def test_w3c_object_element(self):
        body = get_testdata("w3c", "microdata.object.html")
        expected = json.loads(
            get_testdata("w3c", "microdata.object.json").decode("UTF-8")
        )

        mde = MicrodataExtractor(strict=True)
        data = mde.extract(body, "http://www.example.com/microdata/test")
        self.assertEqual(data, expected)


class TestMicrodataFlat(unittest.TestCase):

    maxDiff = None

    def test_w3c_5_2(self):
        body = get_testdata("w3c", "microdata.5.2.html")
        expected = json.loads(
            get_testdata("w3c", "microdata.5.2.flat.json").decode("UTF-8")
        )

        mde = MicrodataExtractor(nested=False, strict=True)
        data = mde.extract(body)
        self.assertEqual(data, expected)

    def test_w3c_7_1(self):
        body = get_testdata("w3c", "microdata.7.1.html")
        expected = json.loads(
            get_testdata("w3c", "microdata.7.1.flat.json").decode("UTF-8")
        )

        mde = MicrodataExtractor(nested=False, strict=True)
        data = mde.extract(body, "http://blog.example.com/progress-report")
        self.assertEqual(data, expected)


class TestMicrodataWithText(unittest.TestCase):

    maxDiff = None

    def test_w3c_5_2(self):
        body = get_testdata("w3c", "microdata.5.2.html")
        expected = json.loads(
            get_testdata("w3c", "microdata.5.2.withtext.json").decode("UTF-8")
        )

        mde = MicrodataExtractor(add_text_content=True)
        data = mde.extract(body)
        self.assertEqual(data, expected)


class TestUrlJoin(unittest.TestCase):

    maxDiff = None

    def test_join_none(self):
        body = get_testdata("schema.org", "product.html")
        expected = json.loads(
            get_testdata("schema.org", "product.json").decode("UTF-8")
        )

        mde = MicrodataExtractor()
        data = mde.extract(body)
        self.assertEqual(data, expected)

    def test_join_custom_url(self):
        body = get_testdata("schema.org", "product.html")
        expected = json.loads(
            get_testdata("schema.org", "product_custom_url.json").decode("UTF-8")
        )

        mde = MicrodataExtractor()
        data = mde.extract(body, base_url="http://some-example.com")
        self.assertEqual(data, expected)


class TestItemref(unittest.TestCase):

    maxDiff = None

    def test_join_none(self):
        body = get_testdata("schema.org", "product-ref.html")
        expected = json.loads(
            get_testdata("schema.org", "product-ref.json").decode("UTF-8")
        )

        mde = MicrodataExtractor()
        data = mde.extract(body)
        self.assertEqual(data, expected)


class TestMicrodataWithDescription(unittest.TestCase):
    maxDiff = None

    def test_if_punctuations_in_description_are_correctly_formatted(self):
        body = get_testdata("websites", "microdata-with-description.html")
        expected = json.loads(
            get_testdata("websites", "microdata-with-description.json").decode("UTF-8")
        )

        mde = MicrodataExtractor()
        data = mde.extract(body)

        self.assertEqual(data, expected)
