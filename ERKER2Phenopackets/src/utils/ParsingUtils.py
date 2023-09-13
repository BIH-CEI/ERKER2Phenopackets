import configparser
from datetime import datetime
from typing import Union

from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf import timestamp_pb2
from loguru import logger


def parse_date_string_to_protobuf_timestamp(date_string: str) -> Timestamp:
    """ Parses a date string in format "YYYY-MM-DD" to a protobuf Timestamp object

    :param date_string: Date string in format "YYYY-MM-DD"
    :type date_string: str
    :return: A protobuf Timestamp object
    :rtype: Timestamp
    """
    logger.trace(f'Parsing date string {date_string} to protobuf timestamp')
    iso8601_utc_timestamp = parse_date_string_to_iso8601_utc_timestamp(date_string)
    return parse_iso8601_utc_to_protobuf_timestamp(iso8601_utc_timestamp)


def parse_iso8601_utc_to_protobuf_timestamp(iso8601_utc_timestamp: str) -> Timestamp:
    """
    Parses a ISO8601 UTC timestamp to a protobuf Timestamp object

    :param iso8601_utc_timestamp: ISO 8601 UTC timestamp
    :type iso8601_utc_timestamp: str
    :return: A protobuf Timestamp object
    :rtype: Timestamp
    """
    logger.trace(f'Parsing iso8601 utc timestamp {iso8601_utc_timestamp} to protobuf '
                 f'timestamp')
    timestamp = timestamp_pb2.Timestamp()
    timestamp.FromJsonString(iso8601_utc_timestamp)
    return timestamp


def parse_date_string_to_iso8601_utc_timestamp(date_string: str) -> str:
    """ Parses a date string in format "YYYY-MM-DD" to ISO8601 UTC timestamp

    ISO8601 UTC timestamp format: “YYYY-MM-DDTHH:MM:SSZ”

    :param date_string: Date string in format "YYYY-MM-DD"
    :type date_string: str
    :return: a Timestamp object in iso8601 utc format
    :rtype: str
    """
    logger.trace(f'Parsing date string {date_string} to iso8601 utc timestamp')
    if date_string is None or date_string == '':
        logger.trace('No date string provided. using NO_DATE from config file')
        config = configparser.ConfigParser()
        config.read('../../data/config/config.cfg')
        return config.get('NoValue', 'date')
    try:
        stripped = datetime.strptime(date_string, "%Y-%m-%d")
        formatted = stripped.strftime("%Y-%m-%dT00:00:00.00Z")
        return formatted
    except ValueError:
        # If parsing fails, raise a ValueError
        logger.error(f'Invalid date format. Please use YYYY-MM-DD format. Got'
                     f' {date_string}')
        raise ValueError(f'Invalid date format. Please use YYYY-MM-DD format. Got '
                         f'{date_string}')


def parse_year_month_day_to_protobuf_timestamp(
        year: Union[str, int],
        month: Union[str, int],
        day: Union[str, int]) -> Timestamp:
    """ Parses a date split into year, month and day to a protobuf Timestamp object

    :param year: Year of date
    :type year: Union[str, int]
    :param month: Month of date
    :type month: Union[str, int]
    :param day: Day of date
    :type day: Union[str, int]
    :return: A protobuf Timestamp object
    :rtype: Timestamp
    """
    logger.trace(f'Parsing year {year}, month {month} and day {day} to protobuf '
                    f'timestamp')
    iso8601_utc_timestamp = parse_year_month_day_to_iso8601_utc_timestamp(
        year,
        month,
        day
    )
    return parse_iso8601_utc_to_protobuf_timestamp(iso8601_utc_timestamp)


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
    logger.trace(f'Parsing year {year}, month {month} and day {day} to iso8601 utc '
                    f'timestamp')
    if isinstance(year, str):
        year = int(year)
    if isinstance(month, str):
        month = int(month)
    if isinstance(day, str):
        day = int(day)
    if 0 < month > 12:
        logger.error(f'Month must be between 1 and 12. Got {month}')
        raise ValueError(f'Month must be between 1 and 12. Got {month}')
    if 0 < day > 31:
        logger.error(f'Day must be between 1 and 31. Got {day}')
        raise ValueError(f'Day must be between 1 and 31. Got {day}')

    formatted_date = f'{year:04d}-{month:02d}-{day:02d}T00:00:00.00Z'

    return formatted_date
