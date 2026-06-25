# mypy: disallow_untyped_defs=False
import json
import unittest

from extruct.jsonld import JsonLdExtractor
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

    def test_jsonld_with_html_entities(self):
        """HTML-encoded JSON-LD (e.g. &quot; instead of ") is parsed correctly.

        Some sites incorrectly escape script content as HTML, producing JSON-LD
        with named entities (&quot;, &amp;) or numeric references (&#34;).
        See https://github.com/scrapinghub/extruct/issues/208
        """
        jsonlde = JsonLdExtractor()

        # Named entity &quot; for double-quotes
        body_named = (
            b'<html><body>'
            b'<script type="application/ld+json">'
            b'{&quot;@context&quot;:&quot;http://schema.org/&quot;,'
            b'&quot;@type&quot;:&quot;Product&quot;,'
            b'&quot;name&quot;:&quot;My Product&quot;}'
            b'</script></body></html>'
        )
        data = jsonlde.extract(body_named)
        self.assertEqual(data, [{"@context": "http://schema.org/", "@type": "Product", "name": "My Product"}])

        # Numeric entity &#34; for double-quotes
        body_numeric = (
            b'<html><body>'
            b'<script type="application/ld+json">'
            b'{&#34;@context&#34;:&#34;http://schema.org/&#34;,'
            b'&#34;@type&#34;:&#34;WebPage&#34;}'
            b'</script></body></html>'
        )
        data = jsonlde.extract(body_numeric)
        self.assertEqual(data, [{"@context": "http://schema.org/", "@type": "WebPage"}])

        # &amp; in a value is unescaped to &
        body_amp = (
            b'<html><body>'
            b'<script type="application/ld+json">'
            b'{"@context":"http://schema.org/","@type":"Organization","name":"Foo &amp; Bar"}'
            b'</script></body></html>'
        )
        data = jsonlde.extract(body_amp)
        self.assertEqual(data, [{"@context": "http://schema.org/", "@type": "Organization", "name": "Foo & Bar"}])
