import argparse

from loguru import logger

from ERKER2Phenopackets.src.logging_ import setup_logging


def analyze(data_path, out_dir_name, publish, debug=False):
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
    logger.error('Not implemented yet')
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
        data_path='',  # TODO: data_path,
        out_dir_name='',  # TODO: out_dir_name,
        publish=args.publish,
        debug=(args.debug or args.trace)  # debug mode enabled if either debug or trace
    )


if __name__ == "__main__":
    main()
