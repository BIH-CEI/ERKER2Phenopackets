import configparser
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List
import threading

import phenopackets
import polars as pl
from phenopackets import Phenopacket
from phenopackets import PhenotypicFeature
from phenopackets import VariationDescriptor, Expression
from phenopackets import GeneDescriptor
from phenopackets import Individual, OntologyClass, Disease, TimeElement
from phenopackets import Interpretation, Diagnosis, GenomicInterpretation
from phenopackets import MetaData
from phenopackets import VariantInterpretation
from loguru import logger

from ERKER2Phenopackets.src.utils import calc_chunk_size, split_dataframe, \
    parse_date_string_to_protobuf_timestamp
from ERKER2Phenopackets.src.utils import parse_iso8601_utc_to_protobuf_timestamp


def map_mc4r2phenopackets(
        df: pl.DataFrame,
        cur_time: str,
        num_threads: int = os.cpu_count(),
) -> List[Phenopacket]:
    """Maps MC4R DataFrame to List of Phenopackets.

    Maps the MC4R DataFrame to a list of Phenopackets. Each row in the DataFrame
    represents a single Phenopacket. The Phenopacket.id is the index of the row.
    Uses parallel processing to speed up the mapping.

    :param df: MC4R DataFrame
    :type df: pl.DataFrame
    :param cur_time: string representation of the current time ("YYYY-MM-DD")
    :type cur_time: str
    :param num_threads: Maximum number of threads to use, defaults to the number of CPUs
    :type num_threads: int, optional
    :return: List of Phenopackets
    :rtype: List[Phenopacket]
    """
    # divide the DataFrame into chunks
    chunk_sizes = calc_chunk_size(num_chunks=num_threads, num_instances=df.height)
    chunks = split_dataframe(df=df, chunk_sizes=chunk_sizes)

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        collected_results = list(executor.map(
            _map_chunk,  # function to execute
            chunks, [cur_time] * len(chunks))  # arguments to pass to function
        )

    # Collect results from all threads into a single list
    results = [result for result_list in collected_results for result in result_list]

    return results


def _map_chunk(chunk: pl.DataFrame, cur_time: str, ) -> List[Phenopacket]:
    """Maps a chunk of the MC4R DataFrame to a list of Phenopackets.

    :param chunk: Chunk of the MC4R DataFrame
    :type chunk: pl.DataFrame
    :return: List of Phenopackets
    :rtype: List[Phenopacket]
    """
    thread_id = threading.get_ident()
    logger.info(f'Currently working on thread {thread_id}')

    # metadata creation
    config = configparser.ConfigParser()

    try:
        config.read('../../data/config/config.cfg')
        no_mutation, no_phenotype, no_date, no_omim, created_by = \
            _get_constants_from_config(config)
    except Exception as e1:
        try:
            config.read('ERKER2Phenopackets/data/config/config.cfg')
            no_mutation, no_phenotype, no_date, no_omim, created_by = \
                _get_constants_from_config(config)
        except Exception as e2:
            print(f"Could not find config file. {e1} {e2}")
            exit()

    created = parse_date_string_to_protobuf_timestamp(cur_time)
    logger.debug(type(created))
    meta_data = _create_metadata(
        created_by=created_by,
        created=created,
        names=config.get('Resources', 'formal_names').split(','),
        namespace_prefixes=config.get('Resources', 'namespace_prefixes').split(','),
        urls=config.get('Resources', 'urls').split(','),
        versions=config.get('Resources', 'versions').split(','),
        iri_prefixes=config.get('Resources', 'iri_prefixes').split(','),
    )
    taxonomy = OntologyClass(id='NCBITaxon:9606', label='Homo sapiens')

    phenopackets_list = []
    for row in chunk.rows(named=True):
        phenopacket_id = row['mc4r_id']
        logger.debug(f'{thread_id}: ID: {phenopacket_id}')

        logger.debug(f'{thread_id}: {row["parsed_year_of_birth"]=}')
        logger.debug(f'{thread_id}: {row["parsed_sex"]=}')

        individual = _map_individual(
            phenopacket_id=phenopacket_id,
            year_of_birth=row['parsed_year_of_birth'],
            sex=row['parsed_sex'],
            taxonomy=taxonomy
        )

        # PHENOTYPIC FEATURES
        hpo_cols = ['sct_8116006_1', 'sct_8116006_2',
                    'sct_8116006_3', 'sct_8116006_4',
                    'sct_8116006_5']
        onset_cols = ['parsed_date_of_phenotyping1', 'parsed_date_of_phenotyping2',
                      'parsed_date_of_phenotyping3', 'parsed_date_of_phenotyping4',
                      'parsed_date_of_phenotyping5']
        label_cols = ['parsed_phenotype_label1', 'parsed_phenotype_label2',
                      'parsed_phenotype_label3', 'parsed_phenotype_label4',
                      'parsed_phenotype_label5']

        phenotypic_features = _map_phenotypic_features(
            # only including cols if they are in the keyset of the row
            hpos=[row[hpo_col] for hpo_col in hpo_cols if hpo_col in row],
            onsets=[row[onset_col] for onset_col in onset_cols if onset_col in row],
            labels=[row[label_col] for label_col in label_cols if label_col in row],
            no_phenotype=no_phenotype,
            no_date=no_date,
        )

        gene_descriptor = _map_gene_descriptor(
            hgnc=row['ln_48018_6_1'],
            symbol=config.get('Constants', 'gene_descriptor_symbol'),
            omims=[
                row['parsed_omim_1'],
                row['parsed_omim_2']
            ],
            no_omim=no_omim
        )

        p_hgvs_cols = ['ln_48005_3_1', 'ln_48005_3_2', 'ln_48005_3_3']
        c_hgvs_cols = ['ln_48004_6_1', 'ln_48004_6_2', 'ln_48004_6_3']

        interpretation = _map_interpretation(
            phenopacket_id=phenopacket_id,
            variant_descriptor_id=config.get('Constants', 'variant_descriptor_id'),
            zygosity=row['parsed_zygosity'],
            allele_label=row['allele_label'],
            # same mutation, p=protein, c=coding DNA reference sequence
            p_hgvs=[row[p_hgvs_col] for p_hgvs_col in p_hgvs_cols if p_hgvs_col in row],
            c_hgvs=[row[c_hgvs_col] for c_hgvs_col in c_hgvs_cols if c_hgvs_col in row],
            no_mutation=no_mutation,
            gene=gene_descriptor
        )

        disease = _map_disease(
            orpha=row['sct_439401001_orpha'],
            date_of_diagnosis=row['parsed_date_of_diagnosis'],
            label=config.get('Constants', 'disease_label'),
            no_date=no_date,
        )

        # Orchestrate the mapping
        phenopacket = Phenopacket(
            id=phenopacket_id,
            subject=individual,
            phenotypic_features=phenotypic_features,
            diseases=[disease],
            meta_data=meta_data,
            interpretations=[interpretation],
        )

        phenopackets_list.append(phenopacket)

    return phenopackets_list


def _create_metadata(created_by: str,
                     created: str,
                     names: List[str],
                     namespace_prefixes: List[str],
                     urls: List[str],
                     versions: List[str],
                     iri_prefixes: List[str],
                     phenopacket_schema_version: str = phenopackets.__version__,
                     ) -> MetaData:
    """Creates the metadata block of the Phenopacket

    https://phenopacket-schema.readthedocs.io/en/latest/metadata.html

    :param created_by: List of authors
    :type created_by: str
    :param created: timestamp phenopacket creation
    :type created: str
    :param names: List of names of the resources used
    :type names: List[str]
    :param namespace_prefixes: List of namespace prefixes of the resources used
    :type namespace_prefixes: List[str]
    :param urls: List of urls of the resources used
    :type urls: List[str]
    :param versions: List of versions of the resources used
    :type versions: List[str]
    :param iri_prefixes: List of iri prefixes of the resources used
    :type iri_prefixes: List[str]
    :param phenopacket_schema_version: version of the phenopacket schema used,
    defaults to phenopackets.__version__ (installed version of phenopackets)
    :type phenopacket_schema_version: str, optional
    :return: Metadata block
    :rtype: MetaData
    """
    resources = []
    for name, namespace_prefix, url, version, iri_prefix in zip(
            names, namespace_prefixes, urls, versions, iri_prefixes):
        resource = phenopackets.Resource(
            id=namespace_prefix,
            name=name,
            namespace_prefix=namespace_prefix,
            url=url,
            version=version,
            iri_prefix=iri_prefix,
        )
        resources.append(resource)

    meta_data = MetaData(
        created_by=created_by,
        created=created,
        phenopacket_schema_version=phenopacket_schema_version,
        resources=resources,
    )
    return meta_data


def _map_individual(phenopacket_id: str,
                    year_of_birth: str,
                    sex: str,
                    taxonomy: OntologyClass
                    ) -> Individual:
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
    :param taxonomy: Taxonomy of the individual (Always human)
    :type taxonomy: OntologyClass
    :return: Individual Phenopacket block
    :rtype: Individual
    """
    year_of_birth_timestamp = parse_iso8601_utc_to_protobuf_timestamp(year_of_birth)
    individual = Individual(
        id=phenopacket_id,
        date_of_birth=year_of_birth_timestamp,
        sex=sex,
        taxonomy=taxonomy,
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
        phenotype = OntologyClass(
            id=hpo,
            label=label
        )
    else:
        phenotype = OntologyClass(
            id=hpo,
        )

    onset_timestamp = parse_iso8601_utc_to_protobuf_timestamp(onset)
    onset = TimeElement(
        timestamp=onset_timestamp
    )

    phenotypic_feature = PhenotypicFeature(
        type=phenotype,
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
    # removing missing vals
    hpos = [hpo for hpo in hpos if not hpo == no_phenotype]
    onsets = [onset for onset in onsets if not onset == no_date]

    # creating phenotypic feature blocks for each hpo code
    phenotypic_features = list(
        map(
            lambda t: _map_phenotypic_feature(hpo=t[0], onset=t[1], label=t[2]),
            zip(hpos, onsets, labels)
        )
    )

    return phenotypic_features


def _map_interpretation(phenopacket_id: str,
                        variant_descriptor_id: str,
                        zygosity: str,
                        allele_label: str,
                        p_hgvs: List[str],
                        c_hgvs: List[str],
                        no_mutation: str,
                        gene: GeneDescriptor) -> VariationDescriptor:
    """Maps ERKER patient data to Interpretation block
    
    Contains info about hgvs, in the VariationDescriptor block

    p.HGVS and c.HGVS is the same mutation, p=protein, c=coding DNA reference sequence

    Phenopackets Documentation of the VariationDescriptor block:
    https://phenopacket-schema.readthedocs.io/en/latest/variant.html

    :param phenopacket_id: ID of the individual
    :type phenopacket_id: str
    :param variant_descriptor_id: ID for the VariantDescriptor block
    :type variant_descriptor_id: str
    :param zygosity: zygosity LOINC code 
    :type zygosity: str
    :param allele_label: human-readable zygosity type
    :type allele_label: str
    :param p_hgvs: List of p.HGVS codes (protein)
    :type p_hgvs: List[str]
    :param c_hgvs: List of c.HGVS codes (coding DNA reference sequence)
    :type c_hgvs: List[str]
    :param gene: GeneDescriptor block
    :type gene: GeneDescriptor
    :return: Interpretation block (containing variation description)
    :rtype: Interpretation
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
        allelic_state=allelic_state,
    )

    variant_interpretation = VariantInterpretation(
        variation_descriptor=variation_descriptor,
    )

    genomic_interpretation_variant = GenomicInterpretation(
        subject_or_biosample_id='subject_id:' + phenopacket_id,
        interpretation_status="UNKNOWN_STATUS",  # TODO: ask daniel
        variant_interpretation=variant_interpretation,
    )

    genomic_interpretation_gene = GenomicInterpretation(
        subject_or_biosample_id='subject_id:' + phenopacket_id,
        interpretation_status="UNKNOWN_STATUS",  # TODO: ask daniel?
        gene=gene,
    )

    diagnosis = Diagnosis(
        genomic_interpretations=[
            genomic_interpretation_gene, genomic_interpretation_variant,
        ]
    )

    interpretation = Interpretation(
        diagnosis=diagnosis
    )
    return interpretation


def _map_gene_descriptor(hgnc: str, symbol: str, omims: List[str], no_omim: str) -> \
        GeneDescriptor:
    """Maps ERKER gene data to GeneDescriptor block

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
    # filter out  null vals
    omims = [omim for omim in omims if not omim == no_omim]

    if omims:  # omims not empty
        gene_descriptor = GeneDescriptor(
            value_id=hgnc,
            symbol=symbol,
            alternate_ids=omims
        )
    else:  # omims empty
        gene_descriptor = GeneDescriptor(
            value_id=hgnc,
            symbol=symbol,
        )

    return gene_descriptor


def _map_disease(
        orpha: str,
        date_of_diagnosis: str,
        label: str,
        no_date: str,
) -> Disease:
    """Maps ERKER patient data to Disease block

    Phenopackets Documentation of the Disease block:
    https://phenopacket-schema.readthedocs.io/en/latest/disease.html#rstdisease

    :param orpha: Orpha code encoding rare disease
    :type orpha: str
    :param date_of_diagnosis: Date of diagnosis
    :type date_of_diagnosis: str
    :param label: human-readable class name
    :type label: str
    :param no_date: symbol for missing date
    :type no_date: str
    :return: Disease Phenopackets block
    """
    term = OntologyClass(
        id=orpha,
        label=label
    )

    # create timestamp for date of diagnosis
    logger.debug(date_of_diagnosis)
    if date_of_diagnosis != no_date:
        date_of_diagnosis_timestamp \
            = parse_iso8601_utc_to_protobuf_timestamp(date_of_diagnosis)
        onset = TimeElement(
            timestamp=date_of_diagnosis_timestamp,
        )

        disease = Disease(
            term=term,
            onset=onset,
        )
    else:
        disease = Disease(
            term=term,
        )

    return disease


def _get_constants_from_config(config):
    no_mutation = config.get('NoValue', 'mutation')
    no_phenotype = config.get('NoValue', 'phenotype')
    no_date = config.get('NoValue', 'date')
    no_omim = config.get('NoValue', 'omim')
    created_by = config.get('Constants', 'creator_tag')

    return no_mutation, no_phenotype, no_date, no_omim, created_by
