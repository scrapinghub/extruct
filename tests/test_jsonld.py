# mypy: disallow_untyped_defs=False
import json
import unittest
from unittest.mock import patch

from extruct.jsonld import JsonLdExtractor, _repair_escapes, _repair_quotes
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

    def test_jsonld_with_unescaped_quotes(self):
        # https://github.com/scrapinghub/extruct/issues/53
        # https://github.com/scrapinghub/extruct/issues/175
        self.assertJsonLdCorrect(
            folder="custom.invalid", page="JSONLD_with_unescaped_quotes"
        )

    def test_jsonld_with_unescaped_quotes_over_several_lines(self):
        # the value itself spans lines, as in the page reported in #175;
        # written inline so the test does not depend on the fixture's newlines
        jsonlde = JsonLdExtractor()
        body = (
            '<script type="application/ld+json">'
            '{"description": "<p style="left">Open daily.\nCall ahead.</p>"}'
            "</script>"
        )
        self.assertEqual(
            jsonlde.extract(body),
            [{"description": '<p style="left">Open daily.\nCall ahead.</p>'}],
        )

    def test_repair_quotes_leaves_valid_json_alone(self):
        for source in [
            '{"a": "x", "b": ["y", "z"], "c": {"d": 1}}',
            r'{"a": "he said \"hi\" loudly"}',
            '{"a": "", "b": "x"}',
            '{"url": "http://x.com/a:b", "n": 1}',
            '{"a": "ends here", "b": 2}',
        ]:
            with self.subTest(source=source):
                self.assertEqual(_repair_quotes(source), source)

    def test_repair_quotes_escapes_inner_quotes(self):
        cases = [
            ('{"a": "two "buttons" here"}', r'{"a": "two \"buttons\" here"}'),
            ('{"a": "<p style="left">x</p>"}', r'{"a": "<p style=\"left\">x</p>"}'),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                self.assertEqual(_repair_quotes(source), expected)

    def test_guessed_quotes_are_logged(self):
        body = (
            '<script type="application/ld+json">'
            '{"a": "two "buttons" here"}'
            "</script>"
        )
        with self.assertLogs("extruct.jsonld", level="WARNING") as cm:
            data = JsonLdExtractor().extract(body)
        self.assertEqual(data, [{"a": 'two "buttons" here'}])
        self.assertIn("Guessed which quotes", cm.output[0])

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

    def test_jsonld_with_named_html_entities(self):
        """See https://github.com/scrapinghub/extruct/issues/208."""
        body = (
            b"<html><body>"
            b'<script type="application/ld+json">'
            b"{&quot;@context&quot;:&quot;http://schema.org/&quot;,"
            b"&quot;@type&quot;:&quot;Product&quot;,"
            b"&quot;name&quot;:&quot;My Product&quot;}"
            b"</script></body></html>"
        )
        self.assertEqual(
            JsonLdExtractor().extract(body),
            [
                {
                    "@context": "http://schema.org/",
                    "@type": "Product",
                    "name": "My Product",
                }
            ],
        )

    def test_jsonld_with_numeric_html_entities(self):
        body = (
            b"<html><body>"
            b'<script type="application/ld+json">'
            b"{&#34;@context&#34;:&#34;http://schema.org/&#34;,"
            b"&#34;@type&#34;:&#34;WebPage&#34;}"
            b"</script></body></html>"
        )
        self.assertEqual(
            JsonLdExtractor().extract(body),
            [{"@context": "http://schema.org/", "@type": "WebPage"}],
        )

    def test_html_entity_in_valid_json_value_stays_literal(self):
        body = (
            b"<html><body>"
            b'<script type="application/ld+json">'
            b'{"@context":"http://schema.org/","@type":"Organization","name":"Foo &amp; Bar"}'
            b"</script></body></html>"
        )
        self.assertEqual(
            JsonLdExtractor().extract(body),
            [
                {
                    "@context": "http://schema.org/",
                    "@type": "Organization",
                    "name": "Foo &amp; Bar",
                }
            ],
        )

    def test_quote_entity_in_valid_json_value_stays_literal(self):
        body = (
            b"<html><body>"
            b'<script type="application/ld+json">'
            b'{"description":"Say &quot;hi&quot;"}'
            b"</script></body></html>"
        )
        self.assertEqual(
            JsonLdExtractor().extract(body),
            [{"description": "Say &quot;hi&quot;"}],
        )

    def test_quote_entity_after_comment_stays_literal(self):
        body = (
            b"<html><body>"
            b'<script type="application/ld+json">'
            b"// generated metadata\n"
            b'{"description":"Say &quot;hi&quot;"}'
            b"</script></body></html>"
        )
        self.assertEqual(
            JsonLdExtractor().extract(body),
            [{"description": "Say &quot;hi&quot;"}],
        )

    def test_unchanged_unescape_reraises_original_error(self):
        original_error = ValueError("original decoder error")
        retry_error = ValueError("duplicate retry error")
        body = '<script type="application/ld+json">not json</script>'

        with patch(
            "extruct.jsonld._iter_jsonld",
            side_effect=[original_error, retry_error],
        ) as iter_jsonld:
            with self.assertRaises(ValueError) as cm:
                JsonLdExtractor().extract(body)

        self.assertIs(cm.exception, original_error)
        self.assertEqual(iter_jsonld.call_count, 1)
