import argparse
import configparser
from datetime import datetime
from pathlib import Path

from loguru import logger

from ..utils import last_phenopackets
from ..logging_ import setup_logging


def analyze(data_path='', out_dir_name='', publish=False, debug=False):
    """Analyse Phenopackets concerning the MC4R gene and its variants.

    TODO @grafea: Please write a short description of what exactly we will analyse
    TODO @grafea: here and why

    :param data_path: Path to a phenopacket file or directory of phenopackets, defaults
        to the last created phenopackets
    :type data_path: str
    :param out_dir_name:
    :type out_dir_name: str
    :param publish:
    :type publish: bool
    :param debug:
    :type debug: bool
    """
    logger.debug(f'{data_path=} {type(data_path)=}')
    logger.debug(f'{out_dir_name=} {type(out_dir_name)=}')
    logger.error('Not implemented yet')

    config = configparser.ConfigParser()
    config.read('ERKER2Phenopackets/data/config/config.cfg')

    if data_path == '':
        data_path = last_phenopackets()

    if publish:
        if out_dir_name:
            out_dir_name = Path(out_dir_name)
        else:
            analysis_out_dir = data_path / 'analysis'
            analysis_out_dir.mkdir(parents=True, exist_ok=True)
            out_dir_name = Path(analysis_out_dir)

        print(out_dir_name)  # TODO: replace this with writing the report to file
    raise NotImplementedError('Not implemented yet')


def main():
    arg_parser = argparse.ArgumentParser(
        prog='analyze',
        description='[WIP] Analyze Phenopackets concerning the MC4R gene and its '
                    'variants.'
    )

    arg_parser.add_argument(
        'path',
        nargs='?',
        default='',
        help='Path to a phenopacket file or directory of phenopackets'
    )

    arg_parser.add_argument(  # TODO: only need this if we want to publish the report
        'out_dir_name',
        nargs='?',
        default='',
        help='The name of the output directory'
    )

    mut_excl_group = arg_parser.add_mutually_exclusive_group()

    mut_excl_group.add_argument('-d', '--debug', action='store_true',
                                help='Enable debug logging')
    mut_excl_group.add_argument('-t', '--trace', action='store_true',
                                help='Enable trace logging')

    arg_parser.add_argument('-p', '--publish', action='store_true',
                            help='Write report to file in out_dir_name')

    args = arg_parser.parse_args()

    if args.debug:
        level = 'DEBUG'
    elif args.trace:
        level = 'TRACE'
    else:
        level = 'INFO'

    setup_logging(level=level)

    analyze(
        data_path=args.path,
        out_dir_name=args.out_dir_name,
        publish=args.publish,
        debug=(args.debug or args.trace)  # debug mode enabled if either debug or trace
    )


if __name__ == "__main__":
    main()
