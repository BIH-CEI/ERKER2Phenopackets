import math
from datetime import datetime

from google.protobuf.internal.well_known_types import Timestamp
from phenopackets import AgeRange, Age


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
    """Parses the sex of a patient entry from ERKER to a Phenopackets sex code.

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

def parse_erker_agerange(age_range: str) -> AgeRange:
    """Parses the age range of a patient entry from ERKER to a Phenopackets AgeRange block

    :param age_range: The age range of the patient.
    :type age_range: str
    :return: An AgeRange Phenopackets block representing the age range of the patient

    col 11: sct_410598002 / age category
    """
    if age_range == 'sct_133931009':
        start = Age(iso8601duration='P0Y')
        end = Age(iso8601duration='P1Y')
    elif age_range == 'sct_410602000':
        start = Age(iso8601duration='P1Y')
        end = Age(iso8601duration='P6Y')
    elif age_range == 'sct_410600008':
        start = Age(iso8601duration='P6Y')
        end = Age(iso8601duration='P12Y')
    elif age_range == 'sct_133937008':
        start = Age(iso8601duration='P12Y')
        end = Age(iso8601duration='P18Y')
    elif age_range == 'sct_13393600':
        start = Age(iso8601duration='P18Y')
        end = Age(iso8601duration='P99Y')
    else:
        print(f'lnc_67162-8_X {age_range}')
        return None

    return AgeRange(start=start, end=end)