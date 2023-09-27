import argparse


def main():
    arg_parser = argparse.ArgumentParser(prog='clear_phenopackets',
                                         description='Removes previously created '
                                                     'phenopackets.')

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

    arg_parser.add_argument('-p', '--publish', action='store_true',
                            help='Write phenopackets to out instead of test')

    # Add positional arguments
    arg_parser.add_argument('data_path', help='The path to the data')
    arg_parser.add_argument('out_dir_name', nargs='?', default='',
                            help='The name of the output directory')

    # Parse the arguments
    args = arg_parser.parse_args()