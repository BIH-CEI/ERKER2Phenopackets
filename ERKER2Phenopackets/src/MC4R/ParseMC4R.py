from google.protobuf.timestamp_pb2 import Timestamp
from . import sex_map_erker2phenopackets, zygosity_map_erker2phenopackets

import re
import configparser

from ERKER2Phenopackets.src.utils import parse_year_month_day_to_iso8601_utc_timestamp
from ERKER2Phenopackets.src.utils import parse_date_string_to_iso8601_utc_timestamp


# 1. method definition
# 2. doc (with examples)
#   a. Title
#   b. description
#   c. parameter & return
#   d. if applicable: examples
# 3. tests
# 4. implement
# 5. activate tests


def parse_year_of_birth(year_of_birth: int) -> Timestamp:
    """Parses a patient's year of birth to ISO8601 UTC timestamp \
    (Required by Phenopackets)
    "YYYY-MM-DD"
    By the Phenopackets documentation it is required to store the date of birth of a 
    subject in a ISO8601 UTC timestamp.

    Could be:
    * “2018-03-01T00:00:00Z” for someone born on an unknown day in March 2018
    * “2018-01-01T00:00:00Z” for someone born on an unknown day in 2018
    * empty if unknown/ not stated.

    Example:
    parse_year_of_birth(2002)
    >>> “2002-01-01T00:00:00.00Z”
    
    Link to Phenopackets documentation, where requirement is defined:
    https://phenopacket-schema.readthedocs.io/en/latest/individual.html

    :param year_of_birth: The year of birth as an integer
    :type year_of_birth: int
    :return: Year of birth formatted as ISO8601 UTC timestamp
    :rtype: Timestamp
    :raises: ValueError: if year_of_birth is not within 1900 and 2023
    """
    if year_of_birth < 1900 or year_of_birth > 2023:
        raise ValueError(f'year_of_birth has to be within 1900 and 2023,'
                         f'but was {year_of_birth}')
    return parse_year_month_day_to_iso8601_utc_timestamp(year_of_birth, 1, 1)


def parse_date_of_diagnosis(date_of_diagnosis: str) -> Timestamp:
    """Parses a patient's date of diagnosis from ERKER to a Phenopackets Age block

    By the Phenopackets documentation Version 2 the onset of a disease i.e. the time of
    diagnosis can be saved as a TimeElement (Age, Timestamp, TimeInterval). In our data\
    the Timestamp is used.

    Could be: 
    * "2021-06-02T00:00:00.00Z" for someone diagnosed on June 2nd 2021
    * empty if unknown / not stated 

    Example: 
    parse_date_of_diagnosis(2018-04-21): 
    >>> "2018-04-21T00:00:00.00Z"

    Link to Phenopackets documentation, where requirement is defined:
    https://phenopacket-schema.readthedocs.io/en/latest/disease.html 

    :param date_of_diagnosis: Date of diagonsis in YYYY-MM-DD format.
    :type date_of_diagnosis: str
    :return: An Age Phenopackets block representing the age of diagnosis of the patient
    :rtype: Timestamp
    :raises ValueError: If the date of diagnosis is not known
    """
    return parse_date_string_to_iso8601_utc_timestamp(date_of_diagnosis)


def parse_sex(sex: str) -> str:
    """Parses the sex (SNOMED) of a patient entry from ERKER to a Phenopackets sex code.

    :param sex: The sex of the patient.
    :type sex: str
    :return: A string code representing the sex of the patient.
    :raises: Value Error: If the sex string is not a valid SNOMED code

    Could be: 
    'sct_248152002': 'FEMALE',
    'sct_248153007': 'MALE',
    'sct_184115007': 'UNKNOWN_SEX',
    'sct_33791000087105': 'OTHER_SEX',

    Example:
    parse_sex(sct_248152002):
    >>> 'FEMALE'

    Link to Phenopackets documentation, where requirement is defined:
    https://phenopacket-schema.readthedocs.io/en/latest/sex.html 
    """

    if sex in sex_map_erker2phenopackets:
        return sex_map_erker2phenopackets[sex]
    else:
        raise ValueError(f'Unknown sex {sex}')


def parse_phenotyping_date(phenotyping_date: str) -> Timestamp:
    """
    Parses dates of determination of HPO values to ISO8601 UTC timestamp \
    (Required by Phenopackets)

    By the Phenopackets documentation it is required to store the onset of a 
    PhenotypicFeature of a subject in a ISO8601 UTC timestamp.

    Could be:
    * “2018-03-01T00:00:00.00Z” for 
    * empty if unknown/ not stated.

    Example:
    parse_phenotyping_date(2018-04-15)
    >>> “2002-01-01T00:00:00.00Z”

    Link to Phenopackets documentation, where requirement is defined:
    https://phenopacket-schema.readthedocs.io/en/latest/phenotype.html 

    :param phenotyping_date: Date of a phenotype's determination in "YYYY-MM-DD" format
    :type phenotyping_date: str
    :return: Date of determination formatted as ISO8601 UTC timestamp
    :rtype: Timestamp
    :raises: Value Error: If date of determination is not in "YYYY-MM-DD" format
    """
    return parse_date_string_to_iso8601_utc_timestamp(phenotyping_date)


def parse_zygosity(zygosity: str) -> str:
    """
    Parses the zygosity (LOINC) of a patient entry from ERKER to a Phenopackets
    Zygosity code.

    Could be: 
    'ln_LA6705-3' : 'GENO:0000136'
    'ln_LA6706-1': 'GENO:0000135'
    'ln_LA6707-9' : 'GENO:0000134'

    Example:
    parse_zygosity(ln_LA6705-3):
    >>> 'GENO:0000136'

    Link to Phenopackets documentation, where requirement is defined:
    https://phenopacket-schema.readthedocs.io/en/latest/variant.html#rstvariant 

    :param zygosity: The zygosity of the patient's genetic record.
    :type zygosity: str
    :return: A string code representing the zygosity of the patient.
    :raises: Value Error: If the zygosity string is not a valid LOINC code
    """
    if zygosity in zygosity_map_erker2phenopackets:
        return zygosity_map_erker2phenopackets[zygosity]
    else:
        raise ValueError(f'Unknown zygosity {zygosity}')


def parse_omim(omim: str) -> str:
    """
    Parses the OMIM Code of a patient entry from ERKER to the Phenopackets \
    OMIM structure

    Example:
    parse_omim('155541.0024')
    >>> 'OMIM:155541.0024'
    
    parse_omim('271630')
    >>> 'OMIM:271630' 

    Link to Phenopackets documentation, where requirement is defined:
    https://phenopacket-schema.readthedocs.io/en/latest/disease.html 
    
    
    :param omim: OMIM code of the patient's genetic record.
    :type omim: str
    :return: a patient's OMIM code in Phenopacket representation
    :raises: Value Error: If the OMIM string is not a valid OMIM code
    """
    omim = omim.replace("\"", "")

    pattern_with_suffix = r'\d{6}\.\d{4}'
    pattern_with_out_suffix = r'\d{6}'

    if omim is None or omim == 'nan':
        config = configparser.ConfigParser()
        config.read('../../data/config/config.cfg')
        return config.get('NoValue', 'omim')
    elif re.match(pattern_with_suffix, omim) or re.match(pattern_with_out_suffix, omim):
        return 'OMIM:' + omim
    else:
        raise ValueError('The OMIM code does not match format "6d.4d" or "6d".'
                         f'Received: {omim}')
