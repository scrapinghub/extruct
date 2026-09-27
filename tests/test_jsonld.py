# mypy: disallow_untyped_defs=False
import json
import unittest

from extruct.jsonld import JsonLdExtractor, _is_framing_line, _repair_escapes
from tests import get_testdata


class TestJsonLD(unittest.TestCase):
    def test_schemaorg_CreativeWork(self):
        self.assertJsonLdCorrect(folder="schema.org", page="CreativeWork.001")

    def test_songkick(self):
        self.assertJsonLdCorrect(
            folder="songkick",
            page="Elysian Fields Brooklyn Tickets, The Owl Music Parlor, 31 Oct 2015",
        )

    def test_jsonld_empty_item(self):
        self.assertJsonLdCorrect(folder="songkick", page="jsonld_empty_item_test")

    def test_jsonld_with_comments(self):
        for page in ["JoinAction.001", "AllocateAction.001"]:
            self.assertJsonLdCorrect(folder="schema.org.invalid", page=page)

        for page in ["JoinAction.001", "AllocateAction.001"]:
            self.assertJsonLdCorrect(folder="custom.invalid", page=page)

    def test_jsonld_with_control_characters(self):
        self.assertJsonLdCorrect(
            folder="custom.invalid", page="JSONLD_with_control_characters"
        )

    def test_jsonld_with_control_characters_comment(self):
        self.assertJsonLdCorrect(
            folder="custom.invalid", page="JSONLD_with_control_characters_comment"
        )

    def test_jsonld_with_json_including_js_comment(self):
        self.assertJsonLdCorrect(folder="custom.invalid", page="JSONLD_with_JS_comment")

    def assertJsonLdCorrect(self, folder, page):
        body, expected = self._get_body_expected(folder, page)
        self._check_jsonld(body, expected)

    def _get_body_expected(self, folder, page):
        body = get_testdata(folder, "{}.html".format(page))
        expected = get_testdata(folder, "{}.jsonld".format(page))
        return body, json.loads(expected.decode("utf8"))

    def _check_jsonld(self, body, expected):
        jsonlde = JsonLdExtractor()
        data = jsonlde.extract(body)
        self.assertEqual(data, expected)

    def test_null(self):
        page = "null_ld_mock"
        body = get_testdata("misc", "{}.html".format(page))
        expected = json.loads(
            get_testdata("misc", "{}.jsonld".format(page)).decode("UTF-8")
        )

        jsonlde = JsonLdExtractor()
        data = jsonlde.extract(body)
        self.assertEqual(data, expected)

    def test_empty_jsonld_script(self):
        jsonlde = JsonLdExtractor()
        body = '<script type="application/ld+json">   \n\n  </script>'
        data = jsonlde.extract(body)
        self.assertEqual(data, [])

    def test_jsonld_with_invalid_escapes(self):
        # https://github.com/scrapinghub/extruct/issues/171
        self.assertJsonLdCorrect(
            folder="custom.invalid", page="JSONLD_with_invalid_escapes"
        )

    def test_repair_escapes(self):
        backslash = "\\"
        cases = [
            # invalid escapes are repaired
            (r'"Bob\'s"', '"Bob\'s"'),
            (r'"Bob\x27s"', r'"Bob\u0027s"'),
            # any other backslash is doubled, never dropped
            (r'"\u12"', r'"\\u12"'),
            (r'"c:\videos"', r'"c:\\videos"'),
            # valid escapes are left alone
            (r'"x\\y"', r'"x\\y"'),
            (r'"q\"b"', r'"q\"b"'),
            (r'"\u00e9"', r'"\u00e9"'),
            (r'"c:\temp"', r'"c:\temp"'),
            # a "\\" pair is consumed whole, so the next escape is still seen
            ('"x' + backslash * 2 + backslash + "'y\"", '"x' + backslash * 2 + "'y\""),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(_repair_escapes(source), expected)

    def test_valid_escapes_survive_extraction(self):
        jsonlde = JsonLdExtractor()
        body = (
            '<script type="application/ld+json">'
            r'{"path": "C:\\Users\\x", "name": "caf\u00e9"}'
            "</script>"
        )
        self.assertEqual(
            jsonlde.extract(body), [{"path": r"C:\Users\x", "name": "caf\u00e9"}]
        )

    def test_jsonld_with_cdata_section(self):
        # https://github.com/scrapinghub/extruct/issues/143
        self.assertJsonLdCorrect(folder="custom.invalid", page="JSONLD_with_CDATA")

    def test_jsonld_with_framing(self):
        jsonlde = JsonLdExtractor()
        payload = '{"@context": "http://schema.org/", "name": "Lubelska"}'
        expected = [{"@context": "http://schema.org/", "name": "Lubelska"}]
        wrappers = [
            "// <![CDATA[\n{}\n// ]]>",
            "/* <![CDATA[ */\n{}\n/* ]]> */",
            "<![CDATA[\n{}\n]]>",
            "<!--\n{}\n-->",
            "<!--\n{}\n--!>",
            "// leading comment\n{}",
            "{}\n// trailing comment",
        ]
        for wrapper in wrappers:
            with self.subTest(wrapper=wrapper):
                body = '<script type="application/ld+json">{}</script>'.format(
                    wrapper.format(payload)
                )
                self.assertEqual(jsonlde.extract(body), expected)

    def test_is_framing_line(self):
        # HTML allows a comment to end with either "-->" or "--!>"
        for line in ["<!--", "-->", "--!>", "<![CDATA[", "]]>", "// ]]>", "  ", ""]:
            with self.subTest(line=line):
                self.assertTrue(_is_framing_line(line))
        for line in ["{", '"a": 1', "}", "// a real comment"]:
            with self.subTest(line=line):
                self.assertFalse(_is_framing_line(line))

    def test_framing_does_not_touch_slashes_in_values(self):
        jsonlde = JsonLdExtractor()
        body = (
            '<script type="application/ld+json">\n'
            '{\n"url": "http://example.com/a//b"\n}\n'
            "</script>"
        )
        self.assertEqual(jsonlde.extract(body), [{"url": "http://example.com/a//b"}])

    def test_jsonld_with_trailing_brace(self):
        # https://github.com/scrapinghub/extruct/issues/87
        self.assertJsonLdCorrect(
            folder="custom.invalid", page="JSONLD_with_trailing_brace"
        )

    def test_jsonld_with_trailing_junk(self):
        jsonlde = JsonLdExtractor()
        expected = [{"@type": "Product", "name": "a"}]
        for script in [
            '{"@type": "Product", "name": "a"}}',
            '{"@type": "Product", "name": "a"};',
            '[{"@type": "Product", "name": "a"}]}',
            '{"@type": "Product", "name": "a"} oops trailing words',
        ]:
            with self.subTest(script=script):
                body = '<script type="application/ld+json">{}</script>'.format(script)
                self.assertEqual(jsonlde.extract(body), expected)

    def test_jsonld_concatenated_values(self):
        jsonlde = JsonLdExtractor()
        body = (
            '<script type="application/ld+json">'
            '{"@type": "Product", "name": "a"}{"@type": "Offer", "price": "1"}'
            "</script>"
        )
        self.assertEqual(
            jsonlde.extract(body),
            [{"@type": "Product", "name": "a"}, {"@type": "Offer", "price": "1"}],
        )

    def test_jsonld_trailing_junk_is_logged(self):
        body = '<script type="application/ld+json">{"name": "a"} junk</script>'
        with self.assertLogs("extruct.jsonld", level="WARNING") as cm:
            JsonLdExtractor().extract(body)
        self.assertIn("Ignoring 4 trailing characters", cm.output[0])

    def test_truncated_jsonld_still_raises(self):
        jsonlde = JsonLdExtractor()
        for script in ['{"@type": "Product", "name":', "hello world"]:
            with self.subTest(script=script):
                body = '<script type="application/ld+json">{}</script>'.format(script)
                with self.assertRaises(ValueError):
                    jsonlde.extract(body)
