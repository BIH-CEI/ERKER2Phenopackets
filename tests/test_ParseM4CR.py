from MC4R.ParseMC4R import parse_year_of_birth, parse_sex
import pytest

def test_parse_year_of_birth():
    example_yob = 2000
    expected_ret = "2000-01-01T00:00:00Z"

    assert parse_year_of_birth(example_yob) == expected_ret


@pytest.mark.parametrize(
    ('inp', 'expected'),
    (
        ('sct_248153007', 'MALE'),
        ('sct_248152002', 'FEMALE'),
        ('sct_33791000087105', 'OTHER_SEX'),
        ('sct_184115007', 'OTHER_SEX'),
        ('sct_394743007_foetus', 'UNKNOWN_SEX'),
    )
)
def test_parse_sex(inp, expected):
    
    assert parse_sex(inp) == expected