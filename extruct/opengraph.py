import re
import lxml.html


class OpenGraphExtractor(object):
    """OpenGraph extractor following extruct API."""

    def extract(self, htmlstring, url=None, encoding='UTF-8'):
        parser = lxml.html.HTMLParser(encoding=encoding)
        doc = lxml.html.fromstring(htmlstring, parser=parser)
        return list(self.extract_items(doc))

    def extract_items(self, document, *args, **kwargs):
        # OpenGraph defines a web page as a single rich object.
        # TODO: Handle known opengraph namespaces.
        for head in document.xpath('//head'):
            prefix = dict(re.findall(r'\s*(\w+): ([^\s]+)', head.attrib.get('prefix', '')))
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
