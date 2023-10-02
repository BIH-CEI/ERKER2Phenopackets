import argparse
import configparser
from pathlib import Path

from loguru import logger

from ERKER2Phenopackets.src.utils import delete_files_in_folder
from ERKER2Phenopackets.src.logging_ import setup_logging


def clear_dir(all_: bool, experimental: bool, publish: bool):
    """
    Deletes all phenopackets in the out folder. If all_ is True, deletes all
    phenopackets in both out/experimental_phenopackets and out/phenopackets.

    :param all_: If True, deletes all phenopackets in both out/experimental_phenopackets
     and out/phenopackets. If False, deletes all phenopackets in either
        out/experimental_phenopackets or out/phenopackets, depending on the value of
        experimental and publish.
    :type all_: bool
    :param experimental: If True, deletes all phenopackets in out/experimental_phenopack
    ets.
    :type experimental: bool
    :param publish: If True, deletes all phenopackets in out/phenopackets.
    :type publish: bool
    """
    logger.trace(f'Called clear_dir() with args: {all_=}, {experimental=}, {publish=}')

    logger.trace('Reading config file')
    config = configparser.ConfigParser()
    config.read('ERKER2Phenopackets/data/config/config.cfg')

    test_out = Path(config.get('Paths', 'test_phenopackets_out_script'))
    prod_out = Path(config.get('Paths', 'phenopackets_out_script'))
    json_suffix = '.json'

    if all_:
        logger.info('Deleting all phenopackets')
        delete_files_in_folder([test_out, prod_out], json_suffix)
    elif experimental:
        logger.info('Deleting experimental phenopackets')
        delete_files_in_folder(test_out, json_suffix)
    elif publish:
        logger.info('Deleting published phenopackets')
        delete_files_in_folder(prod_out, json_suffix)

    logger.info('Finished clearing directories.')


def main():
    arg_parser = argparse.ArgumentParser(prog='clear_phenopackets',
                                         description='Removes previously created '
                                                     'phenopackets. Defaults to -e.')

    mut_excl_group = arg_parser.add_mutually_exclusive_group()

    mut_excl_group.add_argument('-e', '--experimental', action='store_true',
                                help='Deletes all phenopackets in '
                                     'out/experimental_phenopackets')
    mut_excl_group.add_argument('-p', '--publish', action='store_true',
                                help='deletes all phenopackets in out/phenopackets')
    mut_excl_group.add_argument('-a', '--all', action='store_true',
                                help='Deletes all phenopackets in both '
                                     'out/experimental_phenopackets and '
                                     'out/phenopackets')

    args = arg_parser.parse_args()

    setup_logging(level='INFO')

    if not args.all and not args.experimental and not args.publish:
        logger.debug('No tag given, setting deleting experimental to True')
        clear_dir(all_=False, experimental=True, publish=False)
        return
    clear_dir(all_=args.all, experimental=args.experimental, publish=args.publish)


if __name__ == '__main__':
    main()
