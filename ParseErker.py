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
    nanos = math.floor((ts - seconds) * 1e9)
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


def parse_erker_onset(onset: str) -> str:
    """Parse the onset of a patient entry from ERKER to a Phenopackets onset code

    :param onset: The onset of the patient.
    :type onset: str
    :return: An onset code or a string indicating an unknown onset

    **Congenital Onset Obesity:**
    Obesity that originates from birth due to genetic or inherited factors affecting metabolism and fat storage.

    **Antenatal Onset Obesity:**
    Obesity that develops during fetal development in response to maternal factors such as diet and metabolic conditions
     during pregnancy.

    col14: sct_424850005 / Disease onset (Symptoms)
    """
    onset_dict = {
        'sct_118189007': 'HP:0030674',  # Antenatal onset
        'sct_364586004': 'HP:0003577',  # Congenital onset
        'sct_424850005': 'HP:0003674',  # onset_date #onset
    }
    return onset_dict.get(onset, f'Unknown onset value {onset}')


def parse_erker_datediagnosis(age_dg):
    """
    col 18: sct_423493009 / age of diagnosis
    col 19-21: sct_423493009_y,_m,_d / Date_diagnosis
    """
    datediagnosis_dict = {
        'sct_424850005': 'Date_diagnois',
    }

    if age_dg in datediagnosis_dict:
        return Age(iso8601duration=f'P{age_dg.y}Y{age_dg.m}M')
    else:
        raise ValueError(f'Unknown disease date value {age_dg}')
