# mypy: disallow_untyped_defs=False
import copy
from typing import Any
from urllib.parse import urljoin, urlparse

from extruct.dublincore import get_lower_attrib

# Looks like a structured property of og:locale, but is an array of its own.
_OG_UNSTRUCTURED = {"og:locale:alternate"}


def _og_group_structured(properties):
    """Return *properties* with each structured property, e.g.
    ``og:image:width``, moved into a dict with the preceding occurrence of its
    parent property, e.g. ``og:image``."""
    keys = {k for k, _ in properties}
    parents = {k.rpartition(":")[0] for k in keys if k not in _OG_UNSTRUCTURED} & keys
    grouped = []
    current: dict[str, dict[str, str]] = {}
    for k, v in properties:
        parent = k.rpartition(":")[0]
        if parent in current and k not in _OG_UNSTRUCTURED:
            current[parent].setdefault(k, v)
            continue
        if k in parents:
            current[k] = {k: v}
            v = current[k]
        grouped.append((k, v))
    return grouped


def _og_is_blank(k, v):
    if isinstance(v, dict):
        v = v[k]
    return not v or not v.strip()


def _uopengraph(extracted, with_og_array=False, og_structured=False):
    out = []
    for obj in extracted:
        # In order of appearance in the page
        properties = list(obj["properties"])
        if og_structured:
            properties = _og_group_structured(properties)
        flattened: dict[Any, Any] = {}

        for k, v in properties:
            if k not in flattened.keys():
                flattened[k] = v
            elif not _og_is_blank(k, v):
                # If og_array isn't required add first non empty value
                if not with_og_array:
                    if _og_is_blank(k, flattened[k]):
                        flattened[k] = v
                else:
                    if isinstance(flattened[k], list):
                        flattened[k].append(v)
                    elif not _og_is_blank(k, flattened[k]):
                        flattened[k] = [flattened[k], v]
                    else:
                        flattened[k] = v

        t = flattened.pop("og:type", None)
        if t:
            flattened["@type"] = t
        flattened["@context"] = obj["namespace"]
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


def _udublincore(extracted):
    out = []
    extracted_cpy = copy.deepcopy(extracted)
    for obj in extracted_cpy:
        context = obj.pop("namespaces", None)
        obj["@context"] = context
        elements = obj["elements"]
        for element in elements:
            for key, value in element.items():
                if get_lower_attrib(value) == "type":
                    obj["@type"] = element["content"]
                    obj["elements"].remove(element)
                    break
        out.append(obj)
    return out


def _flatten(element, schema_context):
    if isinstance(element, dict):
        element = flatten_dict(element, schema_context, False)
    elif isinstance(element, list):
        element = [
            flatten_dict(o, schema_context, False) if isinstance(o, dict) else o
            for o in element
        ]
    return element


def flatten_dict(d, schema_context, add_context):
    out = dict(d)
    typ = out.pop("type", None)
    if not typ:
        return d

    if isinstance(typ, list):
        out["@type"] = typ
        context = schema_context
    else:
        context, typ = infer_context(typ, schema_context)
        out["@type"] = typ

    if add_context:
        out["@context"] = context

    props = out.pop("properties", {})
    for field, value in props.items():
        value = _flatten(value, schema_context)
        out[field] = value

    children = out.pop("children", [])
    if children:
        out["children"] = []
    for child in children:
        child = _flatten(child, schema_context)
        out["children"].append(child)
    return out


def infer_context(typ, context="http://schema.org"):
    parsed_context = urlparse(typ)
    if parsed_context.netloc:
        base = "".join([parsed_context.scheme, "://", parsed_context.netloc])
        if parsed_context.path and parsed_context.fragment:
            context = urljoin(base, parsed_context.path)
            typ = parsed_context.fragment.strip("/")
        elif parsed_context.path:
            context = base
            typ = parsed_context.path.strip("/")
    return context, typ
