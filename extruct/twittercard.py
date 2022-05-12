import re

from extruct.utils import parse_html


_PREFIX_PATTERN = re.compile(r'\s*(\w+):\s*([^\s]+)')
_TW_NAMESPACES = {
    'twitter': 'https://dev.twitter.com/cards#',
    'schema': 'http://schema.org/',
    'product': 'http://ogp.me/ns/product#',
    'music': 'http://ogp.me/ns/music#',
    'video': 'http://ogp.me/ns/video#',
    'article': 'http://ogp.me/ns/article#',
    'book': 'http://ogp.me/ns/book#',
    'profile': 'http://ogp.me/ns/profile#',
}

class TwitterCardExtractor(object):
    """TwitterCard extractor following extruct API.
    """


    def extract(self, htmlstring, base_url=None, encoding='UTF-8'):
        tree = parse_html(htmlstring, encoding=encoding)
        return list(self.extract_items(tree, base_url=base_url))

    def extract_items(self, document, base_url=None):
        # TwitterCard defines a web page as a single rich object.
        for head in document.xpath('//head'):
            html_elems = document.head.xpath("parent::html")
            namespaces = self.get_namespaces(
                html_elems[0]) if html_elems else {}
            namespaces.update(self.get_namespaces(head))
            props = []
            for el in head.xpath('meta[@name and @content]'):
                prop = el.attrib['name']
                val = el.attrib['content']
                ns = prop.partition(':')[0]
                if ns in _TW_NAMESPACES:
                    namespaces[ns] = _TW_NAMESPACES[ns]
                if ns in namespaces:
                    props.append((prop, val))
            if props:
                yield {'namespace': namespaces, 'properties': props}


    def get_namespaces(self, element):
        return dict(
            _PREFIX_PATTERN.findall(element.attrib.get('prefix', ''))
        )
        