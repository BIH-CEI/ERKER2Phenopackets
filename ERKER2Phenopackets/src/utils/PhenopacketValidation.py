import argparse
import subprocess
import configparser
import os
from pathlib import Path
from typing import Tuple, List, Union
import configparser

from ERKER2Phenopackets.src.logging_ import setup_logging
from loguru import logger


def validate(path: Path = '') -> Union[Tuple[bool, str], List[Tuple[bool, str]]]:
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

    if path == '':
        out_dirs = [
            Path(config.get('Paths', 'phenopackets_out_script')),
            Path(config.get('Paths', 'test_phenopackets_out_script'))
        ]

        subdirectories = []
        for out_dir in out_dirs:
            subdirectories = subdirectories + [
                os.path.join(out_dir, entry) for entry in os.listdir(out_dir)
                if os.path.isdir(os.path.join(out_dir, entry))
            ]

        sorted_directories = sorted(subdirectories, key=os.path.getmtime, reverse=True)
        path = Path(sorted_directories[0])

        if not path or not path.is_dir():
            logger.error('No path to data provided. Please provide a path to the data '
                         'as a command line argument.')
            raise ValueError('No path to data provided. Please provide a path to the '
                             'data as a command line argument.')

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
                cur_ret = _validate_phenopacket(
                    file_path, command, phenopacket_json_path_placeholder
                )
                ret_list.append(cur_ret)

        if not ret_list:
            logger.error(f'Directory {path} does not contain any json files')
            raise ValueError(f'Directory {path} does not contain any json files')

        num_invalid = sum([not ret[0] for ret in ret_list])
        logger.info(f'Number of invalid phenopackets: {num_invalid}')

    logger.info('Finished validating phenopackets')
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
    printed_intro_for_file = False

    def intro_for_file(printed_yet: bool) -> bool:
        if not printed_yet:
            logger.info(f'Validation output of {path}:')
            return True
        return False

    # Print the captured output
    for line in outputs:  # errors
        split_line = line.split(',')

        if line and split_line[1] == 'ERROR':
            printed_intro_for_file = intro_for_file(printed_intro_for_file)

            err = ' '.join(split_line[2:])

            logger.error(err)
            validation_results += 'ERROR:' + err + '\n'
            no_errors = False

        elif line:  # no errors
            printed_intro_for_file = intro_for_file(printed_intro_for_file)
            logger.info(line)
            validation_results += line + '\n'
        else:
            logger.trace(f'No errors found in {path.name}')

    return no_errors, validation_results


def main():

    arg_parser = argparse.ArgumentParser(
        prog='validate',
        description='Validates a phenopacket file or directory of phenopackets. '
                    'By default validates directory of last created phenopackets.'
    )

    arg_parser.add_argument(
        'path',
        nargs='?',
        default='',
        help='Path to a phenopacket file or directory of phenopackets'
    )

    args = arg_parser.parse_args()

    setup_logging(level='INFO')
    logger.debug(f'{args.path=}')

    if args.path:
        logger.debug('if args.path: in if')
        logger.info('Validating phenopackets')

        path = Path(args.path)
    else:
        logger.debug('if args.path: in else')
        path = ''

    validate(path)
