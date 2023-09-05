from datetime import datetime


def parse_date_string_to_iso8601_utc_timestamp(date_string: str) -> str:
    """ Parses a date string in format "YYYY-MM-DD" to ISO8601 UTC timestamp

    :param date_string: Date string in format "YYYY-MM-DD"
    :return:
    """
    try:
        stripped = datetime.strptime(date_string, "%Y-%m-%d")
        formatted = stripped.strftime("%Y-%m-%dT00:00:00.00Z")
        return formatted
    except ValueError:
        # If parsing fails, raise a ValueError
        raise ValueError("Invalid date format. Please use YYYY-MM-DD format.")


def parse_year_month_day_to_iso8601_utc_timestamp(year: int, month: int, day: int) -> \
        str:
    """ Parses a date split into year, month and day to ISO8601 UTC timestamp

    :param year: Year of date
    :type year: int
    :param month: Month of date
    :type month: int
    :param day: Day of date
    :type day: int
    :return: Date formatted as ISO8601 UTC timestamp
    :rtype: str
    """
    formatted_date = f'{year:04d}-{int(month):02d}-{day:02d}T00:00:00.00Z'

    return formatted_date
