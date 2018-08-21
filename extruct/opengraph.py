import re
import lxml.html


_PREFIX_PATTERN = re.compile(r'\s*(\w+): ([^\s]+)')
_OG_NAMESPACES = {
    'og': 'http://ogp.me/ns#',
    'music': 'http://ogp.me/ns/music#',
    'video': 'http://ogp.me/ns/video#',
    'article': 'http://ogp.me/ns/article#',
    'book': 'http://ogp.me/ns/book#',
    'profile': 'http://ogp.me/ns/profile#',
}


def _merge_dicts(dict1, dict2):
    return {**dict1, **dict2}


class OpenGraphExtractor(object):
    """OpenGraph extractor following extruct API."""

    def extract(self, htmlstring, base_url=None, encoding='UTF-8'):
        parser = lxml.html.HTMLParser(encoding=encoding)
        doc = lxml.html.fromstring(htmlstring, parser=parser)
        return list(self.extract_items(doc, base_url=base_url))

    def extract_items(self, document, base_url=None):
        # OpenGraph defines a web page as a single rich object.
        for head in document.xpath('//head'):
            namespaces = dict(
                _PREFIX_PATTERN.findall(head.attrib.get('prefix', ''))
            )
            props = []
            for el in head.xpath('meta[@property and @content]'):
                prop = el.attrib['property']
                val = el.attrib['content']
                ns = prop.partition(':')[0]
                if ns in _OG_NAMESPACES:
                    namespaces[ns] = _OG_NAMESPACES[ns]
                if ns in namespaces:
                    props.append((prop, val))
            if props:
                yield {'namespace': namespaces, 'properties': props}
