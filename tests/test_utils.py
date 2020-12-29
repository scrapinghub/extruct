from sys import version_info

from pytest import mark, raises

from extruct.utils import parse_json


@mark.parametrize(
    'input,output',
    [
        (
            '{"a": ["10\'5""]}',
            {'a': ['10\'5"']},
        ),
        (
            '{"a": ["Say "Hello""]}',
            {'a': ['Say "Hello"']},
        ),
    ]
)
def test_parse_json(input, output):
    if version_info >= (3,):
        assert parse_json(input) == output
    else:
        with raises(ValueError):
            parse_json(input)
