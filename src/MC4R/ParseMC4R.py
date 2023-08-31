# 1. method definition
# 2. doc (with examples)
#   a. Title
#   b. description
#   c. parameter & return
#   d. if applicable: examples
# 3. tests
# 4. implement

def parse_year_of_birth(year_of_birth: int) -> str:
    """Parses a patient's year of birth to ISO8601 UTC timestamp \
    (Required by Phenopackets)

    By the Phenopackets documentation it is required to store the date of birth of a 
    subject in a ISO8601 UTC timestamp.

    Could be:
    * “2018-03-01T00:00:00Z” for someone born on an unknown day in March 2018
    * “2018-01-01T00:00:00Z” for someone born on an unknown day in 2018
    * empty if unknown/ not stated.

    Example:
    parse_year_of_birth(2002)
    >>> “2002-01-01T00:00:00Z”
    
    Link to Phenopackets documentation, where requirement is defined:
    https://phenopacket-schema.readthedocs.io/en/latest/individual.html

    :param year_of_birth: The year of birth as an integer
    :type year_of_birth: int
    :return: Year of birth formatted as ISO8601 UTC timestamp
    :rtype: str
    """
    pass