import math
from datetime import datetime

from google.protobuf.internal.well_known_types import Timestamp


def parse_erker_date_of_birth(age) -> Timestamp:
    """Maps the age of a patient entry from ERKER to a Timestamp object.

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

def parse_erker_sex(sex: str) -> str:
    """Parses the sex of a patient entry from ERKER to a FHIR code.

    :param sex: The sex of the patient.
    :type sex: str
    col 8: sct_281053000 / Sex at birth
    """
    sexdict = {
        'sct_248152002': 'FEMALE',
        'sct_248153007': 'MALE',

        'sct_184115007': 'OTHER_SEX',  # Unbestimmt
        'sct_33791000087105': 'OTHER_SEX',  # Divers
        'sct_394743007_foetus': 'UNKNOWN_SEX'  # Fötus (unbekannt)
    }
    if sex in sexdict:
        return sexdict[sex]
    else:
        raise ValueError(f'Unknown sex value {sex}')