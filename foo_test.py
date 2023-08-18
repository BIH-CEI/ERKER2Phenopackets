import foo
import pytest

@pytest.mark.parametrize(
    ('inp', 'expected'),
    (
            (5, 25),
            (-3., 9),
    )
)
def test_square(inp, expected):
    assert foo.square(inp) == expected
