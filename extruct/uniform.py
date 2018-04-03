from six.moves.urllib.parse import urlparse, urljoin

def _uopengraph(extracted):
    out = []
    for obj in extracted:
        # FIXME: Handle objects in order.
        # FIXME: Handle arrays (repeated properties).
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
            res.append(_flatten_dict(obj, schema_context, True))
    if isinstance(extracted, dict):
        res.append(_flatten_dict(extracted, schema_context, False))

    return res


def _flatten_dict(d, schema_context, add_context):
    typ = d.get('type', None)
    if not typ:
        return d

    if isinstance(typ, list):
        assert len(typ), "Multiple types not supported, storing the first one"
        typ = typ[0]

    context, typ = _infer_context(typ, schema_context)

    out = {k: v for (k, v) in d.items() if k not in ['type', 'properties']}
    out['@type'] = typ
    if add_context:
        out['@context'] = context

    props = d.get('properties') or {}
    for field, value in props.items():
        if isinstance(value, dict):
            value = _flatten_dict(value, schema_context, False)
        elif isinstance(value, list):
            value = [
                _flatten_dict(o, schema_context, False)
                if isinstance(o, dict) else o
                for o in value
            ]
        out[field] = value
    return out


def _rdfa(extracted):



def _infer_context(c, default='http://schema.org'):
    parsed_context = urlparse(c)
    context, typ = default, c # default if cannot be inferred
    if parsed_context.netloc:
        base = ''.join([parsed_context.scheme, '://', parsed_context.netloc])
        if parsed_context.path and parsed_context.fragment:
            context = urljoin(base, parsed_context.path)
            typ = parsed_context.fragment.strip('/')
        elif parsed_context.path:
            context = base
            typ = parsed_context.path.strip('/')
    return context, typ
    
