from six.moves.urllib.parse import urlparse, urljoin


def _uopengraph(extracted):
    out = []
    for obj in extracted:
        flattened = dict(obj['properties'])
        t = flattened.pop('og:type', None)
        if t:
            flattened['@type'] = t
        flattened['@context'] = obj['namespace']
        out.append(flattened)
    return out


def _umicrodata_microformat(extracted, schema_context):
    res = []
    if isinstance(extracted, list):
        for obj in extracted:
            res.append(flatten_dict(obj, schema_context, True))
    elif isinstance(extracted, dict):
        res.append(flatten_dict(extracted, schema_context, False))

    return res


def flatten_dict(d, schema_context, add_context):
    out = dict(d)
    typ = out.pop('type', None)
    if not typ:
        return d

    if isinstance(typ, list):
        out['@type'] = typ
        context = schema_context
    else:
        context, typ = infer_context(typ, schema_context)
        out['@type'] = typ
    
    if add_context:
        out['@context'] = context

    props = out.pop('properties', {})
    for field, value in props.items():
        if isinstance(value, dict):
            value = flatten_dict(value, schema_context, False)
        elif isinstance(value, list):
            value = [
                flatten_dict(o, schema_context, False)
                if isinstance(o, dict) else o
                for o in value
            ]
        out[field] = value
    return out


def infer_context(typ, context='http://schema.org'):
    parsed_context = urlparse(typ)
    if parsed_context.netloc:
        base = ''.join([parsed_context.scheme, '://', parsed_context.netloc])
        if parsed_context.path and parsed_context.fragment:
            context = urljoin(base, parsed_context.path)
            typ = parsed_context.fragment.strip('/')
        elif parsed_context.path:
            context = base
            typ = parsed_context.path.strip('/')
    return context, typ