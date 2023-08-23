import math
from datetime import datetime

from google.protobuf.internal.well_known_types import Timestamp


def parse_erker_date_of_birth(age) -> Timestamp:
    """Maps the age of a patient to a Timestamp object.

    :param age: The age of the patient in years.
    :type age: int or str
    :return: A Timestamp object representing the date of birth.
    col 6: sct_184099003_y / Birthyear

    The value should be an int or str, e.g. 2004
    """
    if isinstance(age, int):
        age = str(age)
    elif isinstance(age, str):
        pass
    else:
        raise ValueError(f'Expected either int or str but got {type(age)}')

    dob = datetime.strptime(age, '%Y')
    ts = dob.timestamp()  # ts is a float
    seconds = math.floor(ts)
    nanos = math.floor((ts-seconds) * 1e9)
    return Timestamp(seconds=seconds, nanos=nanos)