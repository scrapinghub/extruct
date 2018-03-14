import re

import lxml.html

import functools
from .transform import clean_missing
from .schemaorg import (
    schemaorg,
    schemaorg_nested,
    schemaorg_instock,
)

def opengraph_transform(opengraph_entries):
    """
    Transform opengraph product data into schema.org
    See: https://developers.facebook.com/docs/reference/opengraph/object-type/product/

    TODO:
    - map original_price and sale_price
    - map color, condition, weight
    """
    for entry in opengraph_entries:
        def f(query):
            return (entry.get('og:'+query, None) or
                    entry.get('product:'+query, None))

        if f('type') != 'product':
            continue

        out = schemaorg('Product', dict(
            description=f('description'),
            image=f('image'),
            name=f('title'),
            url=f('url'),

            brand=f('brand'),
            category=f('category'),
            gtin12=f('upc'),
            gtin13=f('ean')
        ))
        offer = schemaorg_nested('AggregateOffer', dict(
            availability=f('availability'),
            price=f('price:amount'),
            currency=f('price:currency'),
            sku=f('retailer_part_no'),
            mpn=f('mfr_part_no'),
            seller=f('retailer_title')
        ))
        out['offers'] = [offer]

        yield [clean_missing(out, missing=None)]



class OpenGraphExtractor(object):
    """OpenGraph extractor following extruct API."""

    def extract(self, htmlstring, url='http://www.example.com/', encoding='UTF-8'):
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
