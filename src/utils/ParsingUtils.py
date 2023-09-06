import configparser
from datetime import datetime
from typing import Union


def parse_date_string_to_iso8601_utc_timestamp(date_string: str) -> str:
    """ Parses a date string in format "YYYY-MM-DD" to ISO8601 UTC timestamp

    ISO8601 UTC timestamp format: “YYYY-MM-DDTHH:MM:SSZ”

    :param date_string: Date string in format "YYYY-MM-DD"
    :return:
    """
    if date_string is None or date_string == '':
        config = configparser.ConfigParser()
        config.read('../../data/config/config.cfg')
        return config.get('NoValue', 'date')
    try:
        stripped = datetime.strptime(date_string, "%Y-%m-%d")
        formatted = stripped.strftime("%Y-%m-%dT00:00:00.00Z")
        return formatted
    except ValueError:
        # If parsing fails, raise a ValueError
        raise ValueError("Invalid date format. Please use YYYY-MM-DD format.")


def parse_year_month_day_to_iso8601_utc_timestamp(
        year: Union[str, int],
        month: Union[str, int],
        day: Union[str, int]) -> str:
    """ Parses a date split into year, month and day to ISO8601 UTC timestamp

    :param year: Year of date
    :type year: Union[str, int]
    :param month: Month of date
    :type month: Union[str, int]
    :param day: Day of date
    :type day: Union[str, int]
    :return: Date formatted as ISO8601 UTC timestamp
    :rtype: str
    :raises: ValueError: If month is not between 1 and 12 or day is not between 1 and 31
    """
    if isinstance(year, str):
        year = int(year)
    if isinstance(month, str):
        month = int(month)
    if isinstance(day, str):
        day = int(day)
    if 0 < month > 12:
        raise ValueError(f'Month must be between 1 and 12. Got {month}')
    if 0 < day > 31:
        raise ValueError(f'Day must be between 1 and 31. Got {day}')

    formatted_date = f'{year:04d}-{month:02d}-{day:02d}T00:00:00.00Z'

    return formatted_date
