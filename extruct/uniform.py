from six.moves.urllib.parse import urlparse, urljoin


def _uopengraph(extracted, with_og_arr=False):
    out = []
    for obj in extracted:
      properties = list(reversed(obj['properties']))
      # Set of non empty properties
      non_empty_props = {k for k, v in properties if v and v.strip()}
      # Set of repeated properties with at least 2 non empty values
      repeated_props = {}
      if with_og_arr:
        repeated_props = {k for k in non_empty_props if len([i for i,v in properties if i==k and (v and v.strip())]) > 1}
      # Add properties that is either duplicated but has only 1 non empty value
      # or has only empty values
      flattened = {k: v for k, v in properties
                       if k not in repeated_props and (k not in non_empty_props or (v and v.strip()))}
      if with_og_arr:
        # Add list suffix for those with duplicated and non empty values
        for k in repeated_props: flattened[k+"_list"] = []
        for k, v in properties:
          if k in repeated_props:
            flattened[k+"_list"].append(v)
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


def _flatten(element, schema_context):
    if isinstance(element, dict):
        element = flatten_dict(element, schema_context, False)
    elif isinstance(element, list):
        element = [
            flatten_dict(o, schema_context, False)
            if isinstance(o, dict) else o
            for o in element
        ]
    return element


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
        value = _flatten(value, schema_context)
        out[field] = value

    children = out.pop('children', [])
    if children:
        out['children'] = []
    for child in children:
        child = _flatten(child, schema_context)
        out['children'].append(child)
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
