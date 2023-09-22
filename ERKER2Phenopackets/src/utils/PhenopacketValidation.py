import subprocess
from pathlib import Path
from typing import Tuple, List, Union
import configparser

from phenopackets import Phenopacket
from loguru import logger


def validate(path: Path) -> Union[Tuple[bool, str], List[Tuple[bool, str]]]:
    """Validates a phenopacket file or directory of phenopackets

    This function validates a phenopacket file or directory of phenopackets.
    It checks if the phenopacket file or all phenopackets in the directory
    are valid phenopackets using the `phenopacket-tools` CLI.

    :param path: Path to a phenopacket file or directory of phenopackets
    :type path: Path
    :return: Tuple of a boolean and an error message
    :rtype: Tuple[bool, str]
    :raises ValueError: If the path is not a file or directory
    :raises ValueError: If the path is a file but not a json file
    """
    config = configparser.ConfigParser()
    config.read('ERKER2Phenopackets/data/config/config.cfg')

    jar_path = str(Path(config.get('Paths', 'jar_path')).resolve())
    command = config.get('CLICommands', 'validate')

    jar_path_placeholder = config.get('Placeholders', 'jar_path')
    phenopacket_json_path_placeholder = \
        config.get('Placeholders', 'phenopacket_json_path')

    command = command.replace(jar_path_placeholder, jar_path)
    ret_list = []
    if path.is_file():
        if path.suffix == '.json':
            return _validate_phenopacket(
                path, command, phenopacket_json_path_placeholder
            )
        else:
            logger.error(f'File {path} is not a json file')
            raise ValueError(f'File {path} is not a json file')
    elif path.is_dir():
        for file_path in path.iterdir():
            if file_path.suffix == '.json':
                ret_list.append(_validate_phenopacket(
                    file_path, command, phenopacket_json_path_placeholder
                ))
            return ret_list


def _validate_phenopacket(path: Path, command: str,
                          phenopacket_json_path_placeholder: str) -> Tuple[bool, str]:
    """Validates a single phenopacket

    This function validates a single phenopacket using the `phenopacket-tools`
    CLI. It returns a boolean and an error message.

    :param path: Path to a phenopacket file
    :type path: Path
    :param command: Command to validate a phenopacket
    :type command: str
    :param phenopacket_json_path_placeholder: Placeholder for the path to the
        phenopacket file
    :type phenopacket_json_path_placeholder: str
    :return: Tuple of a boolean and an error message
    :rtype: Tuple[bool, str]
    """

    command = command.replace(phenopacket_json_path_placeholder, str(path.resolve()))
    output = subprocess.check_output(command, shell=True, text=True)

    # Print the captured output
    print(output)

    return False, 'a'
