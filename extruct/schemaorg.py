"""Schema.org function helpers."""
import functools


def make_object(context, type_):
    """Create a JSON+LD object.__"""
    return {
        '@context': context,
        '@type': type_,
    }


def schemaorg(type_, spec, context='http://schema.org'):
    """Create a schema.org object with given type."""
    if context:
        doc = make_object(context, type_)
    else:
        doc = {'@type': type_}

    doc.update(spec)
    return doc


# Nested objects have no context by default.
schemaorg_nested = functools.partial(schemaorg, context=None)


def schemaorg_instock(stock, prefix='http://schema.org/'):
    if stock and isinstance(stock, int) and stock > 0:
        return prefix + 'InStock'
    return prefix + 'OutOfStock'
