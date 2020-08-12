from sys import version_info

from pytest import mark

from extruct.utils import parse_json


@mark.skipif(version_info < (3,), reason="requires Python 3")
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
    assert parse_json(input) == output
