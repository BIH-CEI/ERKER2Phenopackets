import configparser
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List

import polars as pl
from phenopackets import Phenopacket
from phenopackets import Individual, OntologyClass
from phenopackets import VariationDescriptor, Expression

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

        config = configparser.ConfigParser()
        config.read('../../data/config/config.cfg')
        no_mutation = config.get('NoValue', 'mutation')
        no_phenotype = config.get('NoValue', 'phenotype')
        no_date = config.get('NoValue', 'date')
        no_omim = config.get('NoValue', 'omim')
        print(no_mutation, no_phenotype, no_date, no_omim)

        # TODO: Implement mapping
        individual = _map_individual(
            phenopacket_id=phenopacket_id,
            year_of_birth='test',
            sex='test'
        )
        print(individual)

        variation_descriptor = _map_variation_descriptor(
            zygosity=row['parsed_zygosity'],
            allele_label=row['allele_label'],
            # same mutation, p=protein, c=coding DNA reference sequence
            p_hgvs=['ln_48005_3_1', 'ln_48005_3_2', 'ln_48005_3_3'],
            c_hgvs=['ln_48006_6_1', 'ln_48006_6_2', 'ln_48006_6_3'],
            ref_allele='GRCh38 (hg38)',
            no_mutation=no_mutation
        )
        print(variation_descriptor)
    raise NotImplementedError
    # return []


def _map_individual(phenopacket_id: str, year_of_birth: str, sex: str) -> Individual:
    """Maps ERKER patient data to Individual block

    Phenopackets Documentation of the Individual block:
    https://phenopacket-schema.readthedocs.io/en/latest/individual.html
    ?highlight=ref%20allele#hgvs

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


def _map_variation_descriptor(variant_descriptor_id: str,
                              zygosity: str,
                              allele_label: str,
                              p_hgvs: List[str],
                              c_hgvs: List[str],
                              ref_allele: str,
                              no_mutation: str) -> VariationDescriptor:
    """Maps ERKER patient data to VariationDescriptor block

    p.HGVS and c.HGVS is the same mutation, p=protein, c=coding DNA reference sequence

    Phenopackets Documentation of the VariationDescriptor block:
    https://phenopacket-schema.readthedocs.io/en/latest/variant.html

    :param variant_descriptor_id: ID for the VariantDescriptor block
    :type variant_descriptor_id: str
    :param zygosity:
    :type zygosity: str
    :param allele_label: human-readable zygosity type
    :type allele_label: str
    :param p_hgvs: List of p.HGVS codes (protein)
    :type p_hgvs: List[str]
    :param c_hgvs: List of c.HGVS codes (coding DNA reference sequence)
    :type c_hgvs: List[str]
    :param ref_allele:
    :type ref_allele: str
    :return: VariationDescriptor block
    :rtype: VariationDescriptor
    """
    # filter hgvs lists to avoid null vals
    p_hgvs = [p_hgvs[i] for i in range(len(p_hgvs)) if not p_hgvs[i] == no_mutation]
    c_hgvs = [c_hgvs[i] for i in range(len(c_hgvs)) if not c_hgvs[i] == no_mutation]
    hgvs = p_hgvs + c_hgvs

    # create new expression for each hgvs code
    expressions = list(
        map(
            lambda hgvs_element: Expression(syntax='hgvs', value=hgvs_element),
            hgvs
        )
    )

    allelic_state = OntologyClass(
        id=zygosity,
        label=allele_label
    )
    variation_descriptor = VariationDescriptor(
        id=variant_descriptor_id,
        expressions=expressions,
        allelicState=allelic_state

    )
    return variation_descriptor
