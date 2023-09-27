from loguru import logger
import configparser

config = configparser.ConfigParser()
try:
    config.read('../../data/config/config.cfg')
    not_recorded = config.get('NoValue', 'recorded')
    logger.trace('Successfully read config file from default location')
except Exception as e1:
    logger.trace(f'Could not find config file in default location. {e1}')
    try:
        logger.trace('Trying to read config file from alternative location')
        config.read('ERKER2Phenopackets/data/config/config.cfg')
        not_recorded = config.get('NoValue', 'recorded')
        logger.trace('Successfully read config file from alternative location')
    except Exception as e2:
        logger.error(f'Could not find config file. {e1} {e2}')
        exit()

sex_map_erker2phenopackets = {
    'sct_248152002': 'FEMALE',
    'sct_248153007': 'MALE',
    'sct_184115007': 'UNKNOWN_SEX',  # Unbestimmt
    'sct_33791000087105': 'OTHER_SEX',  # Divers
}

zygosity_map_erker2phenopackets = {
    'ln_LA6705-3': 'GENO:0000136',  # homozygous
    'ln_LA6706-1': 'GENO:0000135',  # heterozygous
    'ln_LA6707-9': 'GENO:0000134',  # hemizygous
    'sct_1220561009': 'GENO:0000137',  # unspecified zygosity
}

allele_label_map_erker2phenopackets = {
    'ln_LA6705-3': 'homozygous',
    'ln_LA6706-1': 'heterozygous',
    'ln_LA6707-9': 'hemizygous',
    'sct_1220561009': 'unspecified zygosity',

}

phenotype_label_map_erker2phenopackets = {
    "HP:0025501": 'Class III obesity',
    "HP:0025500": 'Class II obesity',
    "HP:0025499": 'Class I obesity',
    "HP:0025502": 'Overweight',
    "HP:0001513": 'Obesity',
}

phenotype_status_map_erker2phenopackets = {
    "sct_410605003": 'False',
    "sct_723511001": 'True',
    "sct_1220561009": not_recorded
}
