import pytest

from src.MC4R.ParseMC4R import parse_year_of_birth, parse_sex, parse_phenotyping_date, \
parse_date_of_diagnosis, parse_zygosity


def test_parse_year_of_birth():
    example_yob = 2000
    expected_ret = "2000-01-01T00:00:00Z"

    assert parse_year_of_birth(example_yob) == expected_ret


def test_parse_date_of_diagnosis(): 
    example_y = 2004
    example_m = "04"
    example_d = 21
    expected_ret = "2004-04-21T00:00:00.00Z"

    assert parse_date_of_diagnosis(example_y, example_m, example_d) == expected_ret

    
@pytest.mark.parametrize(
    ('inp', 'expected'),
    (
            ('sct_248153007', 'MALE'),
            ('sct_248152002', 'FEMALE'),
            ('sct_33791000087105', 'OTHER_SEX'),
            ('sct_184115007', 'UNKNOWN_SEX'),
    )
)
def test_parse_sex(inp, expected):
    assert parse_sex(inp) == expected

    
    
def test_parse_phenotyping_date():
    parsed_date = "2019-04-16"
    expected_ret = "2019-04-16T00:00:00.00Z"
    
    assert parse_phenotyping_date(parsed_date) == expected_ret


@pytest.mark.parametrize(
    ('inp', 'expected'),
    (
            ('ln_LA6705-3', 'GENO:0000136'),
            ('ln_LA6706-1', 'GENO:0000135'),
            ('ln_LA6707-9', 'GENO:0000134')

    )
)
def test_parse_zygosity(inp, expected):
    assert parse_zygosity(inp) == expected
