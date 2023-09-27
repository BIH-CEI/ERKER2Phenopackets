import polars as pl  # the same as pandas just faster
from ERKER2Phenopackets.src.MC4R.MapMC4R import _map_chunk
from loguru import logger

import configparser
import argparse
from pathlib import Path
from datetime import datetime
import re

from ERKER2Phenopackets.src.logging_ import setup_logging
from ERKER2Phenopackets.src.utils import write_files
from ERKER2Phenopackets.src.utils import PolarsUtils
from ERKER2Phenopackets.src.MC4R.MappingDicts import \
    phenotype_label_map_erker2phenopackets
from ERKER2Phenopackets.src.MC4R.MappingDicts import allele_label_map_erker2phenopackets
from ERKER2Phenopackets.src.MC4R import zygosity_map_erker2phenopackets, \
    sex_map_erker2phenopackets, phenotype_status_map_erker2phenopackets
from ERKER2Phenopackets.src.MC4R.ParseMC4R import parse_date_of_diagnosis, \
    parse_year_of_birth, parse_phenotyping_date, parse_omim
from ERKER2Phenopackets.src.MC4R import map_mc4r2phenopackets


def main():
    """This method reads in a dataset in erker format (mc4r) and writes
    the resulting phenopackets to json files on disk"""
    # Create the parser
    arg_parser = argparse.ArgumentParser(prog='pipeline',
                                         description='A pipeline to map ERKER data in '
                                                     '.csv format to phenopackets.')

    mut_excl_group = arg_parser.add_mutually_exclusive_group()

    mut_excl_group.add_argument('-d', '--debug', action='store_true',
                                help='Enable debug logging')
    mut_excl_group.add_argument('-t', '--trace', action='store_true',
                                help='Enable trace logging')

    arg_parser.add_argument('-p', '--publish', action='store_true',
                            help='Write phenopackets to out instead of test')

    # Add positional arguments
    arg_parser.add_argument('data_path', help='The path to the data')
    arg_parser.add_argument('out_dir_name', nargs='?', default='',
                            help='The name of the output directory')

    # Parse the arguments
    args = arg_parser.parse_args()

    # Check the flags
    if args.debug:
        level = 'DEBUG'
    elif args.trace:
        level = 'TRACE'
    else:
        level = 'INFO'

    setup_logging(level=level)

    if args.publish:
        print('Will write phenopackets to out')

    logger.info('Starting MC4R pipeline')
    out_dir_name = ''
    if args.data_path:  # path do data provided
        data_path = args.data_path

        if args.out_dir_name:  # output path provided
            out_dir_name = args.out_dir_name
            disallowed_chars_pattern = r'[<>:"/\\|?*]'

            if re.search(disallowed_chars_pattern, out_dir_name):
                logger.warning('Removing invalid characters from your directory name: '
                               f'{out_dir_name} . Directory names may not contain the '
                               'following characters: <>:"/\\|?*')

            out_dir_name = re.sub(disallowed_chars_pattern, '', out_dir_name)

            if out_dir_name == ' ' or out_dir_name is None:
                logger.warning('Your directory name is invalid.')
                out_dir_name = ''
    else:
        logger.critical('No path to data provided. Please provide a path to the data '
                        'as a command line argument.')
        return

    pipeline(
        data_path=data_path,
        out_dir_name=out_dir_name,
        publish=args.publish,
        debug=(args.debug or args.trace)  # debug mode enabled if either debug or trace
    )


def pipeline(
        data_path: str,
        out_dir_name: str = '',
        publish: bool = False,
        debug: bool = False
):
    logger.info(f'Data path: {data_path}')
    if out_dir_name:
        logger.info(f'Output directory name: {out_dir_name}')
    else:
        logger.info('No output directory name provided, current time will be used as '
                    'output directory name')

    logger.trace('Reading config file')
    config = configparser.ConfigParser()
    config.read('ERKER2Phenopackets/data/config/config.cfg')

    if publish:
        phenopackets_out = Path(config.get('Paths', 'phenopackets_out_script'))
    else:
        phenopackets_out = Path(config.get('Paths', 'test_phenopackets_out_script'))
    logger.trace('Finished reading config file')
    logger.debug(phenopackets_out.resolve())

    cur_time = datetime.now().strftime("%Y-%m-%d-%H%M")
    logger.debug(f'Current time: {cur_time}')

    # Read data in
    logger.info('Reading data')
    df = pl.read_csv(data_path)
    logger.info(f'Read {len(df)} rows')

    # Null value analysis
    logger.info('Preprocessing data')
    PolarsUtils.null_value_analysis(df, verbose=False)

    # Preprocessing
    df = PolarsUtils.drop_null_cols(df, remove_all_null=True, remove_any_null=False)

    df.drop_in_place('record_id')
    logger.info('Dropped record_id column, since it was not unique.')
    df = PolarsUtils.add_id_col(df, id_col_name='mc4r_id', id_datatype=str)
    logger.info('Added mc4r_id as ID column')

    # Parsing step
    logger.info('Start parsing data for phenopacket creation')
    no_mutation = config.get('NoValue', 'mutation')
    no_phenotype = config.get('NoValue', 'phenotype')
    no_date = config.get('NoValue', 'date')
    no_omim = config.get('NoValue', 'omim')

    # sct_184099003_y (year of birth)
    logger.trace('Parsing year of birth column')
    df = PolarsUtils.map_col(df, map_from='sct_184099003_y',
                             map_to='parsed_year_of_birth',
                             mapping=parse_year_of_birth)

    # sct_281053000 (sex)
    logger.trace('Parsing sex column')
    df = PolarsUtils.map_col(df, map_from='sct_281053000', map_to='parsed_sex',
                             mapping=sex_map_erker2phenopackets)

    # sct_432213005 (date of diagnosis)
    logger.trace('Parsing date of diagnosis column')
    df = PolarsUtils.map_col(df, map_from='sct_432213005',
                             map_to='parsed_date_of_diagnosis',
                             mapping=parse_date_of_diagnosis)
    logger.trace('Filling null values in date of diagnosis column')
    df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_diagnosis', no_date)

    # ln_48007_9_1, ln_48007_9_2, ln_48007_9_3 (zygosity)
    logger.trace('Parsing zygosity column')
    df = PolarsUtils.map_col(df, map_from='ln_48007_9_1', map_to='parsed_zygosity_1',
                             mapping=zygosity_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='ln_48007_9_1', map_to='allele_label_1',
                             mapping=allele_label_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='ln_48007_9_2', map_to='parsed_zygosity_2',
                             mapping=zygosity_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='ln_48007_9_2', map_to='allele_label_2',
                             mapping=allele_label_map_erker2phenopackets)
    if 'ln_48007_9_3' in df.columns:
        df = PolarsUtils.map_col(df, map_from='ln_48007_9_3',
                                 map_to='parsed_zygosity_3',
                                 mapping=zygosity_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='ln_48007_9_3', map_to='allele_label_3',
                             mapping=allele_label_map_erker2phenopackets)

    # sct_439401001_orpha (diagnosis (ORPHA))
    logger.trace('Diagnosis (ORPHA) column does not require parsing')
    # does not require mapping

    # sct_439401001_omim_g_1, sct_439401001_omim_g_2, sct_439401001_omim_g_3 \
    # (Primärdiagnose OMIM)
    logger.trace('Parsing OMIM columns')
    df = PolarsUtils.map_col(df, map_from='sct_439401001_omim_g_1',
                             map_to='parsed_omim_1', mapping=parse_omim)
    df = PolarsUtils.map_col(df, map_from='sct_439401001_omim_g_2',
                             map_to='parsed_omim_2', mapping=parse_omim)

    logger.trace('Filling null values in OMIM columns')
    df = PolarsUtils.fill_null_vals(df, 'parsed_omim_1', no_omim)
    df = PolarsUtils.fill_null_vals(df, 'parsed_omim_2', no_omim)

    # ln_48005_3_1, ln_48005_3_2, ln_48005_3_3 (mutation p.HGVS)
    logger.trace('Filling null values in mutation (p.HGVS) columns')
    df = PolarsUtils.fill_null_vals(df, 'ln_48005_3_1', no_mutation)
    df = PolarsUtils.fill_null_vals(df, 'ln_48005_3_2', no_mutation)
    if 'ln_48005_3_3' in df.columns:
        df = PolarsUtils.fill_null_vals(df, 'ln_48005_3_3', no_mutation)

    # ln_48004_6_1, ln_48004_6_2, ln_48004_6_3 (mutation c.HGVS)
    logger.trace('Filling null values in mutation (c.HGVS) columns')
    df = PolarsUtils.fill_null_vals(df, 'ln_48004_6_1', no_mutation)
    df = PolarsUtils.fill_null_vals(df, 'ln_48004_6_2', no_mutation)
    if 'ln_48004_6_3' in df.columns:
        df = PolarsUtils.fill_null_vals(df, 'ln_48004_6_3', no_mutation)

    # ln_48018_6_1 (gene HGNC)
    # does not require mapping
    logger.trace('HGNC column does not require parsing')

    # sct_8116006_1, sct_8116006_2, sct_8116006_3, sct_8116006_4, \
    # sct_8116006_5 (phenotype classification)
    logger.trace('Filling null values in phenotype classification columns')
    df = PolarsUtils.fill_null_vals(df, 'sct_8116006_1', no_phenotype)
    df = PolarsUtils.fill_null_vals(df, 'sct_8116006_2', no_phenotype)
    df = PolarsUtils.fill_null_vals(df, 'sct_8116006_3', no_phenotype)
    df = PolarsUtils.fill_null_vals(df, 'sct_8116006_4', no_phenotype)
    df = PolarsUtils.fill_null_vals(df, 'sct_8116006_5', no_phenotype)

    # sct_8116006_1_date, sct_8116006_2_date, sct_8116006_3_date, sct_8116006_4_date, \
    # sct_8116006_5_date (dates of phenotype determination)
    logger.trace('Parsing date of phenotype determination columns')
    logger.trace('Filling null values in date of phenotype determination columns')
    df = PolarsUtils.map_col(df, map_from='sct_8116006_1_date',
                             map_to='parsed_date_of_phenotyping1',
                             mapping=parse_phenotyping_date)
    df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping1', no_date)

    df = PolarsUtils.map_col(df, map_from='sct_8116006_2_date',
                             map_to='parsed_date_of_phenotyping2',
                             mapping=parse_phenotyping_date)
    df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping2', no_date)

    if 'sct_8116006_3_date' in df.columns:
        df = PolarsUtils.map_col(df, map_from='sct_8116006_3_date',
                                 map_to='parsed_date_of_phenotyping3',
                                 mapping=parse_phenotyping_date)
        df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping3', no_date)

    if 'sct_8116006_4_date' in df.columns:
        df = PolarsUtils.map_col(df, map_from='sct_8116006_4_date',
                                 map_to='parsed_date_of_phenotyping4',
                                 mapping=parse_phenotyping_date)
        df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping4', no_date)

    if 'sct_8116006_5_date' in df.columns:
        df = PolarsUtils.map_col(df, map_from='sct_8116006_5_date',
                                 map_to='parsed_date_of_phenotyping5',
                                 mapping=parse_phenotyping_date)
        df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping5', no_date)

    # sct_8116006_1_status, sct_8116006_2_status, sct_8116006_3_status,\
    # sct_8116006_4_status, sct_8116006_5_status (status of phenotype determination)
    logger.trace('Parsing status of phenotype determination columns')
    logger.trace('Filling null values in status of phenotype determination columns')
    df = PolarsUtils.map_col(df, map_from='sct_8116006_1_status',
                             map_to='parsed_phenotype_status1',
                             mapping=phenotype_status_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_2_status',
                             map_to='parsed_phenotype_status2',
                             mapping=phenotype_status_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_3_status',
                             map_to='parsed_phenotype_status3',
                             mapping=phenotype_status_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_4_status',
                             map_to='parsed_phenotype_status4',
                             mapping=phenotype_status_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_5_status',
                             map_to='parsed_phenotype_status5',
                             mapping=phenotype_status_map_erker2phenopackets)

    # phenotype label
    logger.trace('Parsing phenotype label columns')
    df = PolarsUtils.map_col(df, map_from='sct_8116006_1',
                             map_to='parsed_phenotype_label1',
                             mapping=phenotype_label_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_2',
                             map_to='parsed_phenotype_label2',
                             mapping=phenotype_label_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_3',
                             map_to='parsed_phenotype_label3',
                             mapping=phenotype_label_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_4',
                             map_to='parsed_phenotype_label4',
                             mapping=phenotype_label_map_erker2phenopackets)
    if 'sct_8116006_5' in df.columns:
        df = PolarsUtils.map_col(df, map_from='sct_8116006_5',
                                 map_to='parsed_phenotype_label5',
                                 mapping=phenotype_label_map_erker2phenopackets)
    logger.info('Finished parsing data')

    # Map to Phenopackets
    logger.info('Start mapping data to phenopackets')
    if debug:
        phenopackets = map_chunk(df, cur_time[:10])
    else:
        phenopackets = map_mc4r2phenopackets(df, cur_time[:10])
    logger.info('Finished mapping data to phenopackets')

    # Write to JSON
    if out_dir_name:
        phenopackets_out_dir = phenopackets_out / out_dir_name  # create dir for output
    else:
        phenopackets_out_dir = phenopackets_out / cur_time  # create dir for output

    logger.info(f'Writing phenopackets to {phenopackets_out_dir.resolve()}')
    write_files(phenopackets, phenopackets_out_dir)
    logger.info(f'Successfully wrote {len(phenopackets)} files to disk')
    logger.info('Finished MC4R pipeline')


if __name__ == "__main__":
    main()
