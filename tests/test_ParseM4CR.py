from MC4R.ParseMC4R import parse_year_of_birth

def test_parse_year_of_birth():
    example_yob = 2000
    expected_ret = "2000-01-01T00:00:00Z"

    assert parse_year_of_birth(example_yob) == expected_ret



def test_parse_date_of_diagnosis(): 
    example_y = 2004
    example_m = 4
    example_d = 21
    expected_ret = "2004-04-21T00:00:00Z"

    assert test_parse_date_of_diagnosis(example_y, example_m, example_d) == expected_ret