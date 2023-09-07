import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

import polars as pl
from phenopackets import Phenopacket
from phenopackets import Individual, OntologyClass
from phenopackets import GeneDescriptor

from src.utils import calc_chunk_size, split_dataframe


def map_mc4r2phenopackets(
        df: pl.DataFrame, created_by: str,
        num_threads: int = os.cpu_count(),
) -> List[Phenopacket]:
    """Maps MC4R DataFrame to List of Phenopackets.

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

        gene_descriptor = _map_gene_descriptor(
            hgnc=row['ln_48018_6_1'],
            symbol='MC4R',  # TODO: add to config
            omims=[
                row['sct_439401001_omim_g_1'],
                row['sct_439401001_omim_g_2']
            ],
            no_omim='test' # todo: fill with config val
        )
        print(gene_descriptor)
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


def _map_gene_descriptor(hgnc: str, symbol: str, omims: List[str], no_omim: str) -> \
        GeneDescriptor:
    """Maps ERKER hgnc data to GeneDescriptor block

    Phenopackets Documentation of the GeneDescriptor block:
    https://phenopacket-schema.readthedocs.io/en/latest/gene.html?highlight
    =GeneDescriptor

    :param hgnc: the HGNC gene code of the patient
    :type hgnc: str
    :param omims: List of OMIM codes
    :type omims: List[str]
    :param no_omim: symbol for missing omim
    :type no_omim: str
    :return: GeneDescriptor Phenopackets block
    :rtype: GeneDescriptor
    """
    omims = [omim for omim in omims if not omim == no_omim]  # filter out null vals

    if omims:  # something in omims
        gene_descriptor = GeneDescriptor(
            value_id=hgnc,
            symbold=symbol,
            alternateIds=omims
        )
    else:  # nothing in omims
        gene_descriptor = GeneDescriptor(
            value_id=hgnc,
            symbold=symbol,
        )

    return gene_descriptor
