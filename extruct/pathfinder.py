import itertools


def _flatten(lst):
    return list(itertools.chain.from_iterable(lst))


def _first(obj):
    if obj:
        for el in obj:
            if el:
                return el


def _find(obj, path, default=None):
    head, *tail = path
    if head.endswith('[]'):
        head = head[:-2]
        iterable = True
    else:
        iterable = False

    if head:
        current = obj.get(head, default)
    else:
        current = obj

    if current is default:
        return current

    if iterable and current is None:
        current = []

    if tail:
        if iterable:
            return [
                _find(sub, tail, default=default) for sub in current
            ]
        else:
            return _find(current, tail, default=default)
    else:
        return list(current) if iterable else current


def find(obj, path, default=None):
    """Returns value from object by given dot-path.

    >>> obj = {"a": {"b": [{"v": 1}, {"v": 2}, {}]}}
    >>> find(obj, "x")
    >>> find(obj, "a.b[].v")
    [1, 2, None]
    >>> find([{}, {'a': 1}], ".[].a")
    [None, 1]
    >>> find({"foo": "bar"}, '.')
    {'foo': 'bar'}
    >>> find({"foo": "bar"}, '[]')
    ['foo']

    """
    if isinstance(path, str):
        path = path.split('.')
    return _find(obj, path, default=default)
