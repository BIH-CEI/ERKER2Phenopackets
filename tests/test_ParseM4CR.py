from MC4R.ParseMC4R import parse_year_of_birth


@pytest.mark.skip(reason='Not implemented yet')
def test_parse_year_of_birth():
    example_yob = 2000
    expected_ret = "2000-01-01T00:00:00Z"

    assert parse_year_of_birth(example_yob) == expected_ret