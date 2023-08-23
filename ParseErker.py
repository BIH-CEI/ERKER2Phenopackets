import csv
import math
from datetime import datetime

from google.protobuf.internal.well_known_types import Timestamp
from phenopackets import AgeRange, Age

from MappingDicts import zygosity_dict, datediagnosis_dict, onset_dict, age_range_dict, sexdict


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
    """Parses the sex (SNOMED code) of a patient entry from ERKER to a Phenopackets sex code.

    :param sex: The sex of the patient.
    :type sex: str
    :return: A string code representing the sex of the patient.
    :raises: Value Error: If the sex string is not a valid SNOMED code

    Allowed values are:
    * sct_248152002: female
    * sct_248153007: male
    * sct_184115007: other sex
    * sct_394743007_foetus: unknown sex

    SNOMED Ontology: https://browser.ihtsdotools.org/?perspective=full&conceptId1=270425006&edition=MAIN/2023-07-31&release=&languages=en

    col 8: sct_281053000 / Sex at birth
    """

    if sex in sexdict:
        return sexdict[sex]
    else:
        raise ValueError(f'Unknown sex value {sex}')


def parse_erker_agerange(age_range: str) -> AgeRange:
    """Parses the age range of a patient entry from ERKER to a Phenopackets AgeRange block

    :param age_range: The age range of the patient.
    :type age_range: str
    :return: An AgeRange Phenopackets block representing the age range of the patient
    :raises: Value Error: If the age range string is not a valid SNOMED code

    col 11: sct_410598002 / age category
    """

    if age_range not in age_range_dict.keys():
        print(f'lnc_67162-8_X {age_range}')
        raise ValueError(f'Unknown age range value {age_range}')

    start, end = age_range_dict[age_range]

    return AgeRange(start=start, end=end)


def parse_erker_onset(onset: str) -> str:
    """Parse the onset of a patient entry from ERKER to a Phenopackets onset code

    :param onset: The onset of the patient.
    :type onset: str
    :return: An onset code or a string indicating an unknown onset

    **Congenital Onset Obesity:**
    Obesity that originates from birth due to genetic or inherited factors affecting metabolism and fat storage.
    Code: HP:0003577

    **Antenatal Onset Obesity:**
    Obesity that develops during fetal development in response to maternal factors such as diet and metabolic conditions
     during pregnancy.
     Code: HP:0030674

    col14: sct_424850005 / Disease onset (Symptoms)
    """

    return onset_dict.get(onset, f'Unknown onset value {onset}')


def parse_erker_datediagnosis(age_dg: str):
    """Parses the date of diagnosis of a patient entry from ERKER to a Phenopackets Age block

    :param age_dg: The age of diagnosis of the patient.
    :type age_dg: str
    :return: An Age Phenopackets block representing the age of diagnosis of the patient
    :raises ValueError: If the age of diagnosis is not known

    col 18: sct_423493009 / age of diagnosis
    col 19-21: sct_423493009_y,_m,_d / Date_diagnosis
    """

    if age_dg in datediagnosis_dict:
        return Age(iso8601duration=f'P{age_dg.y}Y{age_dg.m}M')
    else:
        raise ValueError(f'Unknown disease date value {age_dg}')

def parse_erker_zygosity(f, col1, col2):
    """Parses the zygosity of a patient entry from ERKER to a Phenopackets zygosity code

    :param f: The file to read from
    :type f: file
    :param col1: The first column to read from
    :type col1: str
    :param col2: The second column to read from
    :type col2: str
    :return: A string code representing the zygosity of the patient
    :raises ValueError: If the zygosity is not known

    Valid options are:
    * sct_22061001: homozygous
    * sct_14556007: heterozygous

    """
    reader = csv.DictReader(f)
    for row in reader:
        if row[col1] in zygosity_dict or row[col2] in zygosity_dict:
            if row[col1] in zygosity_dict:
                return zygosity_dict[row[col1]]
            else:
                return zygosity_dict[row[col2]]
    raise ValueError(f'Unknown Zygosity value {col1} {col2}')