# mypy: disallow_untyped_defs=False
from pytest import mark, raises

from extruct.utils import _parse_json


@mark.parametrize(
    "input,output",
    [
        # unescaped quotes
        ('{"a": ["10\'5""]}', {"a": ["10'5\""]}),
        ('{"a": ["Say "Hello""]}', {"a": ['Say "Hello"']}),
        ('{"a": "Say "Hello" there"}', {"a": 'Say "Hello" there'}),
        ('{"a": "1. two "buttons".5. Dab!"}', {"a": '1. two "buttons".5. Dab!'}),
        # unescaped quotes combined with what the comment stripping handles
        ('{"a": [1,], "b": ["Say "Hello""]}', {"a": [1], "b": ['Say "Hello"']}),
        ('{\n// note\n"b": ["Say "Hello""]}', {"b": ['Say "Hello"']}),
        ('<!-- note -->{"a": "Say "Hello""}', {"a": 'Say "Hello"'}),
        # a missing comma is indistinguishable from an unescaped quote, and is
        # resolved by merging the values
        ('{"a": ["x" "y"]}', {"a": ['x" "y']}),
    ],
)
def test_parse_json(input, output):
    assert _parse_json(input) == output


@mark.parametrize(
    "input",
    [
        "",
        "not json",
        "{",
        '{"a": [}',
        '{"a": "b"',
    ],
)
def test_parse_json_unfixable(input):
    with raises(ValueError):
        _parse_json(input)
