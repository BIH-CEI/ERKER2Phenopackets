from pathlib import Path
from typing import Tuple
import configparser

from phenopackets import Phenopacket


def validate(path: Path) -> Tuple[bool, str]:
    """Validates a phenopacket file or directory of phenopackets

    This function validates a phenopacket file or directory of phenopackets.
    It checks if the phenopacket file or all phenopackets in the directory
    are valid phenopackets using the `phenopacket-tools` CLI.

    :param path: Path to a phenopacket file or directory of phenopackets
    :type path: Path
    :return: Tuple of a boolean and an error message
    :rtype: Tuple[bool, str]
    """
    # read config file
    config = configparser.ConfigParser()
    config.read('ERKER2Phenopackets/data/config/config.cfg')

    jar_path = str(Path(config.get('Paths', 'jar_path')).resolve())
    command = config.get('CLICommands', 'validate')

    jar_path_placeholder = config.get('Placeholders', 'jar_path')
    phenopacket_json_path_placeholder = \
        config.get('Placeholders', 'phenopacket_json_path')

    # replace the path to the jar file in the command
    command = command.replace(jar_path_placeholder, jar_path)
    # 1. Check if the path leads to a file or a directory
    # 2. If it is a file, check if it is a json file
    # 3. If it is a directory, collect all json files in the directory
    # 4. Check if the json files are valid phenopackets
    # 5. If they are valid, return True and an empty string,
    # else return False and the error message


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

    return False, 'a'
