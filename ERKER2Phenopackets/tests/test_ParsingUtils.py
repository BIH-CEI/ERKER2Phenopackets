import pytest

from ERKER2Phenopackets.src.utils.ParsingUtils import \
    parse_date_string_to_iso8601_utc_timestamp, \
    parse_year_month_day_to_iso8601_utc_timestamp


@pytest.mark.parametrize(
    ('inp', 'exp'),
    (
            ('1998-06-27', '1998-06-27T00:00:00.00Z'),
            ('2000-01-01', '2000-01-01T00:00:00.00Z'),
            ('2023-12-15', '2023-12-15T00:00:00.00Z'),
    )
)
def test_parse_date_string_to_iso8601_utc_timestamp(inp, exp):
    assert parse_date_string_to_iso8601_utc_timestamp(inp) == exp


@pytest.mark.parametrize(
    ('inp_year', 'inp_month', 'inp_day', 'exp'),
    (
            (1998, 6, 27, '1998-06-27T00:00:00.00Z'),
            (2000, 1, 1, '2000-01-01T00:00:00.00Z'),
            (2023, 12, 15, '2023-12-15T00:00:00.00Z'),
    )
)
def test_parse_year_month_day_to_iso8601_utc_timestamp(inp_year, inp_month, inp_day,
                                                       exp):
    assert parse_year_month_day_to_iso8601_utc_timestamp(
        inp_year, inp_month, inp_day) == exp
