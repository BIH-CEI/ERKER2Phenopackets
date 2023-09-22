import pytest

from ERKER2Phenopackets.src.MC4R.ParseMC4R import \
parse_year_of_birth, parse_sex, parse_phenotyping_date, parse_date_of_diagnosis,\
parse_zygosity, parse_omim, parse_phenotyping_status, parse_phenotyping_status

def test_parse_year_of_birth():
    example_yob = 2000
    expected_ret = "2000-01-01T00:00:00.00Z"

    assert parse_year_of_birth(example_yob) == expected_ret


def test_parse_date_of_diagnosis():
    example_date = "2018-04-12"
    expected_ret = "2018-04-12T00:00:00.00Z"
    assert parse_date_of_diagnosis(example_date) == expected_ret


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
    example_date = "2019-04-16"
    expected_ret = "2019-04-16T00:00:00.00Z"

    assert parse_phenotyping_date(example_date) == expected_ret


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
    

@pytest.mark.parametrize(
    ('inp', 'expected'),
    (
        ('155541.0024', 'OMIM:155541.0024'),   
        ('271630', 'OMIM:271630')
    )
)
def test_parse_omim(inp, expected):
    assert parse_omim(inp) == expected
    

@pytest.mark.parametrize(
    ('inp', 'expected'),
    (
        ('sct_410605003', 'False'),
        ('sct_723511001', 'True'),
        ('sct_1220561009', 'NO_PHENOTYPE')
    )
)
def test_parse_ph_status(inp, expected):
    assert parse_phenotyping_status(inp) == expected