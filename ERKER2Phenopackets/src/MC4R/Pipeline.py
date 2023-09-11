import polars as pl # the same as pandas just faster
from loguru import logger

import configparser
from pathlib import Path
from datetime import datetime

from ERKER2Phenopackets.src.utils import write_files
from ERKER2Phenopackets.src.MC4R import map_mc4r2phenopackets
from ERKER2Phenopackets.src.utils import PolarsUtils
from ERKER2Phenopackets.src.MC4R.MappingDicts import phenotype_label_map_erker2phenopackets
from ERKER2Phenopackets.src.MC4R.MappingDicts import allele_label_map_erker2phenopackets
from ERKER2Phenopackets.src.MC4R import zygosity_map_erker2phenopackets, sex_map_erker2phenopackets
from ERKER2Phenopackets.src.MC4R.ParseMC4R import parse_date_of_diagnosis, parse_year_of_birth, \
parse_phenotyping_date, parse_omim
from ERKER2Phenopackets.src.MC4R.MapMC4R import _map_chunk



def pipeline(data_path: Path):
    """This method reads in a dataset in erker format (mc4r) and writes
    the resulting phenopackets to json files on disk"""
    pass

    config = configparser.ConfigParser()
    config.read('../../data/config/config.cfg')
    real_data = False

    if real_data:
        path = Path(config.get('Paths', 'mc4r_path')) 
    else:
        path = Path(config.get('Paths', 'synth_data_path'))

    phenopackets_out = Path(config.get('Paths', 'phenopackets_out'))
    
    cur_time = datetime.now().strftime("%Y-%m-%d-%H%M")
    
    # Set Creator Tag
    created_by = config.get('Constants', 'creator_tag')
    
    #Read data in
    df = pl.read_csv(path)
    
    PolarsUtils.null_value_analysis(df, verbose=True)
    
    #Preprocessing
    df = PolarsUtils.drop_null_cols(df, remove_all_null=True, remove_any_null=False)
    
    df.drop_in_place('record_id')
    df = PolarsUtils.add_id_col(df, id_col_name='mc4r_id', id_datatype = str) 
    
    # Parsing step
    config = configparser.ConfigParser()
    config.read('../../data/config/config.cfg')
    no_mutation = config.get('NoValue', 'mutation')
    no_phenotype = config.get('NoValue', 'phenotype')
    no_date = config.get('NoValue', 'date')
    no_omim = config.get('NoValue', 'omim')

    # sct_184099003_y (year of birth)
    df = PolarsUtils.map_col(df, map_from='sct_184099003_y', \
                             map_to='parsed_year_of_birth',\
        mapping=parse_year_of_birth)

    # sct_281053000 (sex)
    df = PolarsUtils.map_col(df, map_from='sct_281053000', map_to='parsed_sex',\
        mapping=sex_map_erker2phenopackets)

    # sct_432213005 (date of diagnosis)
    df = PolarsUtils.map_col(df, map_from='sct_432213005',\
        map_to='parsed_date_of_diagnosis' ,mapping=parse_date_of_diagnosis)
    df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_diagnosis', no_date)

    # # ln_48007_9 (zygosity)
    df = PolarsUtils.map_col(df, map_from='ln_48007_9', map_to='parsed_zygosity',\
        mapping=zygosity_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='ln_48007_9', map_to='allele_label', \
                            mapping=allele_label_map_erker2phenopackets)


    # sct_439401001_orpha (diagnosis (ORPHA))
    # does not require mapping

    # sct_439401001_omim_g_1, sct_439401001_omim_g_2, sct_439401001_omim_g_3 \
    # (Primärdiagnose OMIM)
    df = PolarsUtils.map_col(df, map_from='sct_439401001_omim_g_1',\
        map_to='parsed_omim_1' ,mapping=parse_omim)
    df = PolarsUtils.fill_null_vals(df, 'parsed_omim_1', no_omim)
        
    df = PolarsUtils.map_col(df, map_from='sct_439401001_omim_g_2',\
        map_to='parsed_omim_2' ,mapping=parse_omim)
    df = PolarsUtils.fill_null_vals(df, 'parsed_omim_2', no_omim)


    # ln_48005_3_1, ln_48005_3_2, ln_48005_3_3 (mutation p.HGVS)
    df = PolarsUtils.fill_null_vals(df, 'ln_48005_3_1', no_mutation)
    df = PolarsUtils.fill_null_vals(df, 'ln_48005_3_2', no_mutation)
    if 'ln_48005_3_3' in df.columns:
        df = PolarsUtils.fill_null_vals(df, 'ln_48005_3_3', no_mutation)

    # ln_48004_6_1, ln_48004_6_2, ln_48004_6_3 (mutation c.HGVS)
    df = PolarsUtils.fill_null_vals(df, 'ln_48004_6_1', no_mutation)
    df = PolarsUtils.fill_null_vals(df, 'ln_48004_6_2', no_mutation)
    if 'ln_48004_6_3' in df.columns:
        df = PolarsUtils.fill_null_vals(df, 'ln_48004_6_3', no_mutation)

    # ln_48018_6_1 (gene HGNC)
    # does not require mapping

    # sct_8116006_1, sct_8116006_2, sct_8116006_3, sct_8116006_4, \
    # sct_8116006_5 (phenotype classification)
    df = PolarsUtils.fill_null_vals(df, 'sct_8116006_1', no_phenotype)
    df = PolarsUtils.fill_null_vals(df, 'sct_8116006_2', no_phenotype)
    df = PolarsUtils.fill_null_vals(df, 'sct_8116006_3', no_phenotype)
    df = PolarsUtils.fill_null_vals(df, 'sct_8116006_4', no_phenotype)
    if 'sct_8116006_5' in df.columns:
        df = PolarsUtils.fill_null_vals(df, 'sct_8116006_5', no_phenotype)

    # sct_8116006_1_date, sct_8116006_2_date, sct_8116006_3_date, sct_8116006_4_date, \
        # sct_8116006_5_date (dates of phenotype determination)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_1_date', \
                             map_to='parsed_date_of_phenotyping1',\
                             mapping=parse_phenotyping_date)
    df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping1',no_date)

    df = PolarsUtils.map_col(df, map_from='sct_8116006_2_date', \
                             map_to='parsed_date_of_phenotyping2', \
                             mapping=parse_phenotyping_date)
    df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping2',no_date)

    if 'sct_8116006_3_date' in df.columns:
        df = PolarsUtils.map_col(df, map_from='sct_8116006_3_date', \
                                 map_to='parsed_date_of_phenotyping3', \
                                 mapping=parse_phenotyping_date)
        df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping3',no_date)
        
    if 'sct_8116006_4_date' in df.columns:
        df = PolarsUtils.map_col(df, map_from='sct_8116006_4_date', \
                                 map_to='parsed_date_of_phenotyping4', \ 
                                 mapping=parse_phenotyping_date)
        df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping4',no_date)
        
    if 'sct_8116006_5_date' in df.columns:
        df = PolarsUtils.map_col(df, map_from='sct_8116006_5_date', \
                                 map_to='parsed_date_of_phenotyping5', \
                                 mapping=parse_phenotyping_date)  
        df = PolarsUtils.fill_null_vals(df, 'parsed_date_of_phenotyping5',no_date)  


    # phenotype label
    df = PolarsUtils.map_col(df, map_from='sct_8116006_1',\
                             map_to='parsed_phenotype_label1',\
                             mapping=phenotype_label_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_2',\
                             map_to='parsed_phenotype_label2',\
                             mapping=phenotype_label_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_3', \
                             map_to='parsed_phenotype_label3', \
                             mapping=phenotype_label_map_erker2phenopackets)
    df = PolarsUtils.map_col(df, map_from='sct_8116006_4', \
                             map_to='parsed_phenotype_label4', \
                             mapping=phenotype_label_map_erker2phenopackets)
    if 'sct_8116006_5' in df.columns:
        df = PolarsUtils.map_col(df, map_from='sct_8116006_5',\
                                 map_to='parsed_phenotype_label5',\ 
                                 mapping=phenotype_label_map_erker2phenopackets)
        
        
    # Map to Phenopackets
    phenopackets = _map_chunk(df, cur_time[:10]) #map_mc4r2phenopackets(df, cur_time)
    
    
    # Write to JSON
    phenopackets_out_dir = phenopackets_out / cur_time # create dir for output

    write_files(phenopackets, phenopackets_out_dir)
    
    
    
    if __name__ ==  "__main__":
    path = input('Type the path to the file')
    path = Path(path)
    pipeline(path)