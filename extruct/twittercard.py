# mypy: disallow_untyped_defs=False
from extruct.utils import parse_html


class TwitterCardExtractor:
    """Twitter Card extractor following extruct API."""

    def extract(self, htmlstring, base_url=None, encoding="UTF-8"):
        tree = parse_html(htmlstring, encoding=encoding)
        return list(self.extract_items(tree, base_url=base_url))

    def extract_items(self, document, base_url=None):
        props = []
        for el in document.xpath("//meta[@content]"):
            key = el.get("name") or el.get("property") or ""
            if key.startswith("twitter:"):
                props.append((key, el.get("content")))
        if props:
            yield {"properties": props}
