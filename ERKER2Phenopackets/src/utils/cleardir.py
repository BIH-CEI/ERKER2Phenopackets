import argparse
import configparser
from pathlib import Path

from ERKER2Phenopackets.src.utils import delete_files_in_folder


def clear_dir(all_: bool, experimental: bool, publish: bool):
    config = configparser.ConfigParser()
    config.read('ERKER2Phenopackets/data/config/config.cfg')

    test_out = Path(config.get('Paths', 'test_phenopackets_out_script'))
    prod_out = Path(config.get('Paths', 'phenopackets_out_script'))
    json_suffix = '.json'

    if all_:
        delete_files_in_folder([test_out, prod_out], json_suffix)
    elif experimental:
        delete_files_in_folder(test_out, json_suffix)
    elif publish:
        delete_files_in_folder(prod_out, json_suffix)


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

    clear_dir(args.all, args.experimental, args.publish)


if __name__ == '__main__':
    main()
