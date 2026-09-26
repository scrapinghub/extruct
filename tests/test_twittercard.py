# mypy: disallow_untyped_defs=False
from extruct.twittercard import TwitterCardExtractor


def test_twittercard():
    html = """<html><head>
    <meta name="twitter:card" content="summary">
    <meta property="twitter:site" content="@example">
    <meta name="twitter:title" property="twitter:title" content="Title">
    <meta name="og:image" content="https://example.com/a.png">
    <meta name="description" content="Description">
    </head><body><meta name="twitter:label1" content="Price"></body></html>"""
    assert TwitterCardExtractor().extract(html) == [
        {
            "properties": [
                ("twitter:card", "summary"),
                ("twitter:site", "@example"),
                ("twitter:title", "Title"),
                ("twitter:label1", "Price"),
            ]
        }
    ]


def test_twittercard_empty():
    html = '<html><head><meta property="og:title" content="Title"></head></html>'
    assert TwitterCardExtractor().extract(html) == []
