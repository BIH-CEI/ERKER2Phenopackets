import numpy as np
from datetime import datetime, timedelta
import random


def date_to_seconds(date):
    """Converts a date string to seconds since 1970-01-01"""
    return (
            datetime.strptime(date, '%Y-%m-%d')
            -
            datetime(1970, 1, 1)  # beginning of unix time
    ).total_seconds()


def seconds_to_date(seconds):
    """Converts seconds since 1970-01-01 to a date string"""
    return datetime.fromtimestamp(seconds).strftime('%Y-%m-%d')


def generate_random_date(start_date, end_date):
    """Generates a random date between start_date and end_date"""
    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

    random_days = random.randint(0, (end_datetime - start_datetime).days)
    random_date = start_datetime + timedelta(days=random_days)

    return random_date.strftime('%Y-%m-%d')


def average_length_of_period(month_lengths_days, x):
    length_periods = []

    for start_month in range(12):
        end_month = (start_month + x) % 12
        if end_month < start_month:
            period = month_lengths_days[start_month:] + month_lengths_days[:end_month]
        else:
            period = month_lengths_days[start_month:end_month]

        length_periods.append(sum(period))

    avg_length = np.average(length_periods)

    if x >= 12:
        avg_length += 365 * (x // 12)
    return avg_length
