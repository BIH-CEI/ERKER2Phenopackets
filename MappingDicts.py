zygosity_dict = {
    'sct_22061001': 'homozygous',
    'sct_14556007': 'heterozygous'
}

datediagnosis_dict = {
    'sct_424850005': 'Date_diagnois',
}

onset_dict = {
    'sct_118189007': 'HP:0030674',  # Antenatal onset
    'sct_364586004': 'HP:0003577',  # Congenital onset
    'sct_424850005': 'HP:0003674',  # onset_date #onset
}

age_range_dict = {
    'sct_133931009': ('P0Y','P1Y'),
    'sct_410602000': ('P1Y','P6Y'),
    'sct_410600008': ('P6Y','P12Y'),
    'sct_133937008': ('P12Y','P18Y'),
    'sct_13393600': ('P18Y','P99Y')
}

sexdict = {
    'sct_248152002': 'FEMALE',
    'sct_248153007': 'MALE',

    'sct_184115007': 'OTHER_SEX',  # Unbestimmt
    'sct_33791000087105': 'OTHER_SEX',  # Divers
    'sct_394743007_foetus': 'UNKNOWN_SEX'  # Fötus (unbekannt)
}