import re
import lxml.html


_PREFIX_PATTERN = re.compile(r'\s*(\w+): ([^\s]+)')
_OG_NAMESPACES = {
    ('og', 'http://ogp.me/ns#'),
    ('music', 'http://ogp.me/ns/music#'),
    ('video', 'http://ogp.me/ns/video#'),
    ('article', 'http://ogp.me/ns/article#'),
    ('book', 'http://ogp.me/ns/book#'),
    ('profile', 'http://ogp.me/ns/profile#'),
}


class OpenGraphExtractor(object):
    """OpenGraph extractor following extruct API."""

    def extract(self, htmlstring, base_url=None, encoding='UTF-8'):
        parser = lxml.html.HTMLParser(encoding=encoding)
        doc = lxml.html.fromstring(htmlstring, parser=parser)
        return list(self.extract_items(doc, base_url=base_url))

    def extract_items(self, document, base_url=None):
        # OpenGraph defines a web page as a single rich object.
        # TODO: Handle known opengraph namespaces.
        for head in document.xpath('//head'):
            prefix = dict(_PREFIX_PATTERN.findall(head.attrib.get('prefix', '')))
            prefix.setdefault('og', 'http://ogp.me/ns#')
            props = []
            for el in head.xpath('meta[@property and @content]'):
                prop = el.attrib['property']
                val = el.attrib['content']
                ns = prop.partition(':')[0]
                if ns in prefix:
                    props.append((prop, val))
            if props:
                yield {'namespace': prefix, 'properties': props}
