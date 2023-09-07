import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

import polars as pl
from phenopackets import Phenopacket
from phenopackets import Individual, OntologyClass
from phenopackets import TimeElement, PhenotypicFeature

from src.utils import calc_chunk_size, split_dataframe


def map_mc4r2phenopackets(
        df: pl.DataFrame, created_by: str,
        num_threads: int = os.cpu_count(),
) -> List[Phenopacket]:
    """
    Map MC4R DataFrame to List of Phenopackets.

    Maps the MC4R DataFrame to a list of Phenopackets. Each row in the DataFrame
    represents a single Phenopacket. The Phenopacket.id is the index of the row.
    Uses parallel processing to speed up the mapping.

    :param df: MC4R DataFrame
    :type df: pl.DataFrame
    :param created_by: Name of creator
    :type created_by: str
    :param num_threads: Maximum number of threads to use, defaults to the number of CPUs
    :type num_threads: int, optional
    :return: List of Phenopackets
    :rtype: List[Phenopacket]
    """
    # divide the DataFrame into chunks
    chunk_sizes = calc_chunk_size(num_chunks=num_threads, num_instances=df.height)
    chunks = split_dataframe(df=df, chunk_sizes=chunk_sizes)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        collected_results = list(executor.map(_map_chunk, chunks))

    # Collect results from all threads into a single list
    results = [result for result_list in collected_results for result in result_list]

    return results


def _map_chunk(chunk: pl.DataFrame) -> List[Phenopacket]:
    for row in chunk.rows(named=True):
        phenopacket_id = row['record_id']

        # TODO: Implement mapping
        individual = _map_individual(
            phenopacket_id=phenopacket_id,
            year_of_birth='test',
            sex='test'
        )
        print(individual)

        # TODO: again not quite sure how to do this, multiple phenotypic features?
        phenotypic_features = _map_phenotypic_features(
            hpos=['sct_8116006_1', 'sct_8116006_2', 'sct_8116006_3',
                  'sct_8116006_4', 'sct_8116006_5'],
            onsets=['sct_8116006_1_date', 'sct_8116006_2_date', 'sct_8116006_3_date',
                    'sct_8116006_4_date', 'sct_8116006_5_date'],
            labels=['PUT LABEL HERE'] * 5 # TODO
        )
        print(phenotypic_features)
    raise NotImplementedError
    # return []


def _map_individual(phenopacket_id: str, year_of_birth: str, sex: str) -> Individual:
    """Maps ERKER patient data to Individual block

    Phenopackets Documentation of the Individual block:
    https://phenopacket-schema.readthedocs.io/en/latest/individual.html

    :param phenopacket_id: ID of the individual
    :type phenopacket_id: str
    :param year_of_birth: Year of birth of the individual
    :type year_of_birth: str
    :param sex: Sex of the individual
    :type sex: str
    :return: Individual Phenopacket block
    :rtype: Individual
    """
    individual = Individual(
        id=phenopacket_id,
        date_of_birth=year_of_birth,
        sex=sex,
        taxonomy=OntologyClass(id='NCBITaxon:9606', label='Homo sapiens')
    )

    return individual


def _map_phenotypic_feature(
        hpo: str, onset: str, label: str = None) -> PhenotypicFeature:
    """Maps ERKER patient data to PhenotypicFeature block

    Phenopackets Documentation of the PhenotypicFeature block:
    https://phenopacket-schema.readthedocs.io/en/latest/phenotype.html

    :param hpo: hpo code
    :type hpo: str
    :param onset: onset date
    :type onset: str
    :param label: human-readable class name, defaults to None
    :type label: str, optional
    :return:
    """
    if label:
        ontology_class = OntologyClass(
            id=hpo,
            label=label
        )
    else:
        ontology_class = OntologyClass(
            id=hpo,
        )

    onset = TimeElement(
        timestamp=onset
    )

    phenotypic_feature = PhenotypicFeature(
        type=ontology_class,
        onset=onset
    )
    return phenotypic_feature


def _map_phenotypic_features(
        hpos: List[str],
        onsets: List[str],
        no_phenotype: str,
        no_date: str,
        labels: List[str] = None) -> List[PhenotypicFeature]:
    """Maps ERKER patient data to PhenotypicFeature block

    Phenopackets Documentation of the PhenotypicFeature block:
    https://phenopacket-schema.readthedocs.io/en/latest/phenotype.html

    :param hpos: list of hpo codes
    :type hpos: List[str]
    :param onsets: list of onset dates
    :type onsets: List[str]
    :param no_phenotype: no phenotype code
    :type no_phenotype: str
    :param no_date: no date code
    :type no_date: str
    :param labels: list of human-readable class names, defaults to None
    :type labels: List[str], optional
    :return: list of PhenotypicFeature Phenopacket blocks
    :rtype: List[PhenotypicFeature]
    """
    # removing missing vals TODO: improve this logic because they can be out of order
    hpos = [hpo for hpo in hpos if not hpo == no_phenotype]
    onsets = [onset for onset in onsets if not onset == no_date]
    phenotypic_features = list(
        map(
            lambda t: _map_phenotypic_feature(
            t[0], t[1], t[2]), zip(hpos, onsets, labels)
        )
    )
    
    return phenotypic_features
