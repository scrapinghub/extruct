from pytest import mark

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
    assert parse_json(input) == output
