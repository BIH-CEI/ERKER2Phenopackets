import subprocess
import sys
import os
from pathlib import Path
from typing import Tuple, List, Union
import configparser

from ERKER2Phenopackets.src.logging_ import setup_logging
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
    :raises ValueError: If the path is a directory but does not contain any json files
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

            if not ret_list:
                logger.error(f'Directory {path} does not contain any json files')
                raise ValueError(f'Directory {path} does not contain any json files')
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
    outputs = output.split('\n')

    no_errors = True
    validation_results = ''

    # Print the captured output
    logger.info(f'Validation output of {path}:')
    for line in outputs:  # errors
        split_line = line.split(',')

        if line and split_line[1] == 'ERROR':
            err = ' '.join(split_line[2:])
            logger.error(err)
            validation_results += 'ERROR:' + err + '\n'
            no_errors = False

        elif line:  # no errors
            logger.info(line)
            validation_results += line + '\n'
            # TODO: see if we can make this nice in the the case  of no errors

    return no_errors, validation_results


def main():
    setup_logging(level='INFO')
    logger.info('Validating phenopackets')
    path = ''
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        directory = Path('ERKER2Phenopackets/data/out/phenopackets')
        subdirectories = \
            [
                os.path.join(directory, entry) for entry in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, entry))
            ]
        sorted_directories = sorted(subdirectories, key=os.path.getmtime, reverse=True)
        path = Path(sorted_directories[0])

        if not path or not path.is_dir():
            logger.error('No path to data provided. Please provide a path to the data '
                         'as a command line argument.')
            raise ValueError('No path to data provided. Please provide a path to the '
                             'data as a command line argument.')
    validate(path)


if __name__ == '__main__':
    validate(Path(r'C:\Users\Surface\OneDrive\Documents\DataSpell\ERKER2Phenopackets'
                  r'\ERKER2Phenopackets\data\out\phenopackets\example-phenopackets-from'
                  r'-synthetic-data\0.json'))
