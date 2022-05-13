import re

from extruct.utils import parse_html


# _PREFIX_PATTERN = re.compile(r'\s*(\w+):\s*([^\s]+)')
_PREFIX_PATTERN = re.compile(r'^\s*(?:<!--\s*)?(?:@|\#)twittercard\s*(?:-->)?\s*$', re.I)
_TW_NAMESPACES = {
    'twitter': 'https://dev.twitter.com/cards#',
    'owl'   : 'http://www.w3.org/2002/07/owl#',
    'gr'    : 'http://purl.org/goodrelations/v1#',
    'ctag'    : 'http://commontag.org/ns#',
    'cc'    : 'http://creativecommons.org/ns#',
    'grddl'   : 'http://www.w3.org/2003/g/data-view#',
    'rif'   : 'http://www.w3.org/2007/rif#',
    'sioc'    : 'http://rdfs.org/sioc/ns#',
    'skos'    : 'http://www.w3.org/2004/02/skos/core#',
    'xml'   : 'http://www.w3.org/XML/1998/namespace',
    'rdfs'    : 'http://www.w3.org/2000/01/rdf-schema#',
    'rev'   : 'http://purl.org/stuff/rev#',
    'rdfa'    : 'http://www.w3.org/ns/rdfa#',
    'dc'    : 'http://purl.org/dc/terms/',
    'foaf'    : 'http://xmlns.com/foaf/0.1/',
    'void'    : 'http://rdfs.org/ns/void#',
    'ical'    : 'http://www.w3.org/2002/12/cal/icaltzd#',
    'vcard'   : 'http://www.w3.org/2006/vcard/ns#',
    'wdrs'    : 'http://www.w3.org/2007/05/powder-s#',
    'og'    : 'http://ogp.me/ns#',
    'wdr'   : 'http://www.w3.org/2007/05/powder#',
    'rdf'   : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'xhv'   : 'http://www.w3.org/1999/xhtml/vocab#',
    'xsd'   : 'http://www.w3.org/2001/XMLSchema#',
    'v'     : 'http://rdf.data-vocabulary.org/#',
    'skosxl'  : 'http://www.w3.org/2008/05/skos-xl#',
    'schema'  : 'http://schema.org/',
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
        