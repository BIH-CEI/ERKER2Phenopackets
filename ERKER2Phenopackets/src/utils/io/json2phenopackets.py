import os
from pathlib import Path
from typing import List, Union

from loguru import logger
from phenopackets import Phenopacket
from google.protobuf.json_format import Parse


def read_json_file2phenopacket(file_path: Union[str, Path]) -> Phenopacket:
    """Reads a Phenopacket from a JSON file.

    :param file_path: The path to the JSON file.
    :type file_path: Union[str, Path]
    :return: The loaded Phenopacket.
    :rtype: Phenopacket
    """
    with open(file_path, 'r') as fh:
        json_data = fh.read()
        phenopacket = Phenopacket()
        Parse(json_data, phenopacket)
        return phenopacket


def read_json_files2phenopackets(dir_path: Union[str, Path]) -> List[Phenopacket]:
    """Reads a list of Phenopackets from JSON files in a directory.

    :param dir_path: The directory containing JSON files.
    :type dir_path: Union[str, Path]
    :return: The list of loaded Phenopackets.
    :rtype: List[Phenopacket]
    """
    logger.trace(f'Called read_json_files2phenopackets in {dir_path}')
    phenopackets_list = []
    for file_name in os.listdir(dir_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(dir_path, file_name)
            phenopacket = read_json_file2phenopacket(file_path)
            phenopackets_list.append(phenopacket)
    return phenopackets_list
