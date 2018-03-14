import logging
import functools
from lxml.html import fromstring
from extruct.jsonld import JsonLdExtractor
from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.opengraph import OpenGraphExtractor
from extruct.microformat import MicroformatExtractor
from extruct.xmldom import XmlDomHTMLParser


logger = logging.getLogger(__name__)


def _microdata_transform(obj, schema_context, add_context=True):
    typ = obj.get('type')
    if isinstance(typ, list):
        assert len(typ), "multiple types not supported"
        typ = typ[0]

    if not typ:
        return obj

    if typ.startswith(schema_context):
        typ = typ[len(schema_context):].strip('/')

    out = {'@type': typ}
    if add_context:
        out['@context'] = schema_context

    props = obj.get('properties') or {}
    for field, value in props.items():
        if isinstance(value, dict):
            value = _microdata_transform(value, schema_context, add_context=False)
        elif isinstance(value, list):
            value = [
                _microdata_transform(o, schema_context, add_context=False)
                if isinstance(o, dict) else o
                for o in value
            ]
        out[field] = value

    return out


def _opengraph_transform(obj):
    """Transform opengraph representation into schema.org-like schema

    This doesn't map opengraph fields into schema.org fields.

    ."""
    # FIXME: Handle objects in order.
    # FIXME: Handle arrays (repeated properties).
    context = obj['namespace']
    out = dict(obj['properties'])
    out['@context'] = context
    return out


def extract(htmlstring, url='http://www.example.com/', encoding="UTF-8", 
            syntaxes="all", schema_context='http://schema.org'):
    domparser = XmlDomHTMLParser(encoding=encoding)
    tree = fromstring(htmlstring, parser=domparser)
    if syntaxes == 'all':
        syntaxes = ['microdata', 'jsonld', 'opengraph', 'microformat', 'rdfa']
    processors = []
    if 'microdata' in syntaxes:
        processors.append(
            ('microdata',
             functools.partial(_microdata_transform, 
                               schema_context=schema_context),
             MicrodataExtractor().extract_items)
             )
    if 'jsonld' in syntaxes:
        processors.append(
            ('jsonld',
             lambda x: x,
             JsonLdExtractor().extract_items)
             )
    if 'opengraph' in syntaxes:
        processors.append(
            ('opengraph',
             _opengraph_transform,
             OpenGraphExtractor().extract_items)
             )
    if 'microformat' in syntaxes:
        processors.append(
            ('microformat',
             functools.partial(_microdata_transform, 
                               schema_context='http://microformats.org/wiki/'),
             MicroformatExtractor().extract_items)
             )
    if 'rdfa' in syntaxes:
        processors.append(
            ('rdfa',
             # TODO: transform rdfa output into something more manageable.
             lambda x: x,
             RDFaExtractor().extract_items)
             )           

    output = {}
    for label, trans, extract in processors:
        try:
            output[label] = [trans(obj) for obj in extract(document=tree, url=url, html=html)]
        except Exception:
            logger.exception("Failed to parse %s", url)
    return output
