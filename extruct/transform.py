"""Transformation helpers."""

missing = object()


def clean_missing(obj, missing=missing):
    """Recursively removes items with missing as value."""
    for key, val in list(obj.items()):
        if val is missing or val == "" or val is None:
            del obj[key]
        elif isinstance(val, dict):
            obj[key] = clean_missing(val, missing=missing)
        elif isinstance(val, list):
            obj[key] = [
                clean_missing(v)
                for v in val
                if (v is not missing and
                    v != "" and
                    v is not None)
            ]
    return obj
