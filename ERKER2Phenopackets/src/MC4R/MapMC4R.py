import configparser
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Union
import threading
import uuid

import phenopackets
import polars as pl
from phenopackets import Phenopacket
from phenopackets import PhenotypicFeature
from phenopackets import VariationDescriptor, Expression
from phenopackets import GeneDescriptor
from phenopackets import Individual, OntologyClass, TimeElement
from phenopackets import Interpretation, Diagnosis, GenomicInterpretation
from phenopackets import MetaData, Disease
from phenopackets import VariantInterpretation
from loguru import logger

from ERKER2Phenopackets.src.utils import calc_chunk_size, split_dataframe, \
    parse_date_string_to_protobuf_timestamp
from ERKER2Phenopackets.src.utils import parse_iso8601_utc_to_protobuf_timestamp

uuid_gen = uuid.uuid4()


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
    logger.trace('Called map_mc4r2phenopackets() with the following parameters:'
                 f'\n\tdf: {df.head(5)}'
                 f'\n\tcur_time: {cur_time}'
                 f'\n\tnum_threads: {num_threads}')

    # divide the DataFrame into chunks
    logger.trace(f'Calculating chunk sizes to split the DataFrame into {num_threads} '
                 'chunks')
    chunk_sizes = calc_chunk_size(num_chunks=num_threads, num_instances=df.height)
    logger.trace(f'Resulting chunk sizes by splitting {df.height} elements into '
                 f'{num_threads} chunks: {chunk_sizes}')
    logger.trace(f'Splitting the DataFrame into {num_threads} chunks')
    chunks = split_dataframe(df=df, chunk_sizes=chunk_sizes)
    logger.trace(f'Finished splitting the DataFrame into {num_threads} chunks')

    logger.trace(f'Creating {num_threads} threads to map the chunks to Phenopackets')
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        collected_results = list(executor.map(
            _map_chunk,  # function to execute
            chunks, [cur_time] * len(chunks))  # arguments to pass to function
        )
    logger.trace('Finished mapping the chunks to Phenopackets')

    # Collect results from all threads into a single list
    results = [result for result_list in collected_results for result in result_list]
    logger.trace('Successfully collected results from all threads')

    logger.trace('Finished map_mc4r2phenopackets()')
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
    logger.trace(f'{thread_id}: Called _map_chunk() with the following parameters:'
                 f'\n\tchunk: {chunk.head(5)}'
                 f'\n\tcur_time: {cur_time}')

    # metadata creation
    config = configparser.ConfigParser()

    logger.debug(f'{thread_id}: CWD: {os.getcwd()}')
    logger.trace(f'{thread_id}: Trying to read config file from default location')
    try:
        config.read('../../data/config/config.cfg')
        no_mutation, no_phenotype, no_date, no_omim, not_recorded, created_by = \
            _get_constants_from_config(config)
        logger.trace(f'{thread_id}: Successfully read config file from default '
                     'location')
    except Exception as e1:
        logger.trace(f'{thread_id}: Could not find config file in default location.'
                     f' {e1}')
        try:
            logger.trace(f'{thread_id}: Trying to read config file from alternative '
                         'location')
            config.read('ERKER2Phenopackets/data/config/config.cfg')
            no_mutation, no_phenotype, no_date, no_omim, not_recorded, created_by = \
                _get_constants_from_config(config)
            logger.trace(f'{thread_id}: Successfully read config file from alternative '
                         'location')
        except Exception as e2:
            logger.error(f'{thread_id}: Could not find config file. {e1} {e2}')
            exit()

    logger.trace(f'{thread_id}: Creating metadata block')
    created = parse_date_string_to_protobuf_timestamp(cur_time)
    meta_data = _create_metadata(
        created_by=created_by,
        created=created,
        names=config.get('Resources', 'formal_names').split(','),
        namespace_prefixes=config.get('Resources', 'namespace_prefixes').split(','),
        urls=config.get('Resources', 'urls').split(','),
        versions=config.get('Resources', 'versions').split(','),
        iri_prefixes=config.get('Resources', 'iri_prefixes').split(','),
    )
    logger.trace(f'{thread_id}: Successfully created metadata block \n {meta_data}')

    logger.trace(f'{thread_id}: Creating taxonomy block')
    taxonomy = OntologyClass(id='NCBITaxon:9606', label='Homo sapiens')
    logger.trace(f'{thread_id}:Successfully created taxonomy block {taxonomy}')

    phenopackets_list = []
    logger.trace(f'{thread_id}: Starting loop to build phenopacket for each patient.')
    for i, row in enumerate(chunk.rows(named=True)):
        logger.trace(f'{thread_id}: Iteration {i + 1}/{chunk.height}')
        logger.trace(f'{thread_id}: Mapping row: {row}')
        phenopacket_id = row['mc4r_id']

        logger.trace(f'{thread_id}: Creating individual block')
        individual = _map_individual(
            phenopacket_id=phenopacket_id,
            year_of_birth=row['parsed_year_of_birth'],
            sex=row['parsed_sex'],
            taxonomy=taxonomy
        )
        logger.trace(f'{thread_id}: Created individual block {individual}')

        # PHENOTYPIC FEATURES
        logger.trace(f'{thread_id}: Creating phenotypic features block')
        hpo_cols = ['sct_8116006_1', 'sct_8116006_2',
                    'sct_8116006_3', 'sct_8116006_4',
                    'sct_8116006_5']
        onset_cols = ['parsed_date_of_phenotyping1', 'parsed_date_of_phenotyping2',
                      'parsed_date_of_phenotyping3', 'parsed_date_of_phenotyping4',
                      'parsed_date_of_phenotyping5']
        label_cols = ['parsed_phenotype_label1', 'parsed_phenotype_label2',
                      'parsed_phenotype_label3', 'parsed_phenotype_label4',
                      'parsed_phenotype_label5']
        status_cols = ['parsed_phenotype_status1', 'parsed_phenotype_status2',
                       'parsed_phenotype_status3', 'parsed_phenotype_status4',
                       'parsed_phenotype_status5']

        phenotypic_features = _map_phenotypic_features(
            # only including cols if they are in the keyset of the row
            hpos=[row[hpo_col] for hpo_col in hpo_cols if hpo_col in row],
            onsets=[row[onset_col] for onset_col in onset_cols if onset_col in row],
            labels=[row[label_col] for label_col in label_cols if label_col in row],
            status=[row[status_col] for status_col in status_cols if status_col in row],
            no_phenotype=no_phenotype,
            no_date=no_date,
            not_recorded=not_recorded,
        )
        logger.trace(f'{thread_id}: Successfully created phenotypic features block '
                     f'{phenotypic_features}')

        # GENE DESCRIPTOR
        logger.trace(f'{thread_id}: Creating gene descriptor block')
        # gene_descriptor = _map_gene_descriptor(
        #     hgnc=row['ln_48018_6_1'],
        #     symbol=config.get('Constants', 'gene_descriptor_symbol'),
        #     omims=[
        #         row['parsed_omim_1'],
        #         row['parsed_omim_2']
        #     ],
        #     no_omim=no_omim
        # )
        # logger.trace(f'{thread_id}: Successfully created gene descriptor block '
        #              f'{gene_descriptor}')

        # DISEASE
        logger.trace(f'{thread_id}: Creating disease block')
        disease = _map_disease_for_diagnosis(
            orpha=row['sct_439401001_orpha'],
            label=config.get('Constants', 'disease_label'),
        )
        # #  activate this if we switch back to Disease block
        # disease = _map_disease_block(
        #     orpha=row['sct_439401001_orpha'],
        #     date_of_diagnosis=row['parsed_date_of_diagnosis'],
        #     label=config.get('Constants', 'disease_label'),
        #     no_date=no_date,
        # )
        logger.trace(f'{thread_id}: Successfully created diagnosis block {disease}')

        # INTERPRETATION
        logger.trace(f'{thread_id}: Creating interpretation block')
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
            # gene=gene_descriptor,
            interpretation_status=config.get('Constants', 'interpretation_status'),
            disease=disease,
        )
        logger.trace(f'{thread_id}: Successfully created interpretation block '
                     f'{interpretation}')

        # Orchestrate the mapping
        logger.trace(f'{thread_id}: Creating phenopacket')
        phenopacket = Phenopacket(
            id=phenopacket_id,
            subject=individual,
            phenotypic_features=phenotypic_features,
            diseases=[disease],
            meta_data=meta_data,
            interpretations=[interpretation],
        )
        logger.trace(f'{thread_id}: Successfully created phenopacket {phenopacket}')

        phenopackets_list.append(phenopacket)

        logger.trace(f'{thread_id}: Appended phenopacket to list')
        logger.trace(f'{thread_id}: Finished mapping row {i + 1}/{chunk.height}')

    logger.trace(f'{thread_id}: Finished loop to build phenopacket for each patient.')
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
    logger.trace(f'Creating metadata block with the following parameters:'
                 f'\n\tcreated_by: {created_by}'
                 f'\n\tcreated: {created}'
                 f'\n\tnames: {names}'
                 f'\n\tnamespace_prefixes: {namespace_prefixes}'
                 f'\n\turls: {urls}'
                 f'\n\tversions: {versions}'
                 f'\n\tiri_prefixes: {iri_prefixes}'
                 f'\n\tphenopacket_schema_version: {phenopacket_schema_version}')
    resources = []
    for name, namespace_prefix, url, version, iri_prefix in zip(
            names, namespace_prefixes, urls, versions, iri_prefixes):
        resource = phenopackets.Resource(
            id=namespace_prefix.strip(),  # strip to remove trailing whitespaces
            name=name.strip(),
            namespace_prefix=namespace_prefix.strip(),
            url=url.strip(),
            version=version.strip(),
            iri_prefix=iri_prefix.strip(),
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
    logger.trace(f'Mapping individual with the following parameters:'
                 f'\n\tphenopacket_id: {phenopacket_id}'
                 f'\n\tyear_of_birth: {year_of_birth}'
                 f'\n\tsex {sex}'
                 f'\n\ttaxonomy: {taxonomy}')

    year_of_birth_timestamp = parse_iso8601_utc_to_protobuf_timestamp(year_of_birth)
    individual = Individual(
        id=phenopacket_id,
        date_of_birth=year_of_birth_timestamp,
        sex=sex,
        taxonomy=taxonomy,
    )

    return individual


def _map_phenotypic_feature(
        hpo: str, onset: str, status: str, not_recorded: str, label: str = None
) -> Union[PhenotypicFeature, None]:
    """Maps ERKER patient data to PhenotypicFeature block

    Phenopackets Documentation of the PhenotypicFeature block:
    https://phenopacket-schema.readthedocs.io/en/latest/phenotype.html
    
    If the status is set to not recorded, this function return None

    :param hpo: hpo code
    :type hpo: str
    :param onset: onset date
    :type onset: str
    :type status: str for confirmed/refuted/not recorded
    :param status: str
    :param not_recorded: not recorded code
    :type not_recorded: str
    :param label: human-readable class name, defaults to None
    :type label: str, optional
    :return: Union[PhenotypicFeature, None]
    """
    logger.trace(f'Mapping phenotypic feature with the following parameters:'
                 f'\n\thpo: {hpo}'
                 f'\n\tonset: {onset}'
                 f'\n\tlabel: {label}'
                 f'\n\tstatus: {status}'
                 f'\n\tnot_recorded: {not_recorded}')

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

    if status != not_recorded:
        status: bool = eval(status)
        phenotypic_feature = PhenotypicFeature(
            type=phenotype,
            onset=onset,
            excluded=status
        )
        return phenotypic_feature
    return None


def _map_phenotypic_features(
        hpos: List[str],
        onsets: List[str],
        no_phenotype: str,
        no_date: str,
        not_recorded: str,
        status: List[str],
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
    :param not_recorded: not recorded code
    :type not_recorded: str
    :param status: string representing confirmed/refuted/not recorded
    :type status: List[str]
    :param labels: list of human-readable class names, defaults to None
    :type labels: List[str], optional
    :return: list of PhenotypicFeature Phenopacket blocks
    :rtype: List[PhenotypicFeature]
    """
    logger.trace(f'Mapping phenotypic features with the following parameters:'
                 f'\n\thpos: {hpos}'
                 f'\n\tonsets: {onsets}'
                 f'\n\tno_phenotype: {no_phenotype}'
                 f'\n\tno_date: {no_date}'
                 f'\n\tstatus: {status}'
                 f'\n\tlabels: {labels}')

    # removing missing vals
    hpos = [hpo for hpo in hpos if not hpo == no_phenotype]
    onsets = [onset for onset in onsets if not onset == no_date]

    # creating phenotypic feature blocks for each hpo code
    phenotypic_features = list(
        map(
            lambda t: _map_phenotypic_feature(hpo=t[0], onset=t[1], label=t[2],
                                              status=t[3], not_recorded=not_recorded),
            zip(hpos, onsets, labels, status)
        )
    )

    # filter out Nones (if the feature has status not recorded, a none object is 
    # returned by the _map_phenotypic_feature method)
    phenotypic_features = [phenotyptic_feature for phenotyptic_feature in
                           phenotypic_features if phenotyptic_feature is not None]

    return phenotypic_features


def _map_interpretation(phenopacket_id: str,
                        variant_descriptor_id: str,
                        zygosity: str,
                        allele_label: str,
                        p_hgvs: List[str],
                        c_hgvs: List[str],
                        no_mutation: str,
                        gene: GeneDescriptor,
                        interpretation_status: str,
                        disease: OntologyClass,
                        ) -> VariationDescriptor:
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
    :param interpretation_status: status of the interpretation
    :type interpretation_status: str
    :param gene: GeneDescriptor block
    :type gene: GeneDescriptor, optional
    :param disease: Disease block
    :type disease: OntologyClass
    :return: Interpretation block (containing variation description)
    :rtype: Interpretation
    """
    logger.trace(f'Mapping interpretation with the following parameters:'
                 f'\n\tphenopacket_id: {phenopacket_id}'
                 f'\n\tvariant_descriptor_id: {variant_descriptor_id}'
                 f'\n\tzygosity: {zygosity}'
                 f'\n\tallele_label: {allele_label}'
                 f'\n\tp_hgvs: {p_hgvs}'
                 f'\n\tc_hgvs: {c_hgvs}'
                 f'\n\tno_mutation: {no_mutation}'
                 f'\n\tgene: {gene}'
                 f'\n\tinterpretation_status: {interpretation_status}')

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
        variation_descriptor=variation_descriptor
    )

    # Right now this handles one variant per
    #  case/phenopacket, right?
    #  However, will this always be the case for the ERKER format?
    #  How about diseases with autosomal recessive mode of inheritance, where
    #  a pair of heterozygous variants can be disease causing (compound heterozygosity)?
    #  In that case, we need to create 2 genomic interpretations, one per variant,
    #  and I am not sure the current
    #  architecture would allow that.

    # in the new version of the ERKER we allow these choices for the zygosity:
    # Homozygous // (simple) Heterozygous // Compound heterozygous //Double heterozygous
    # // Hemizygous // Not recorded (qualifier value)
    # we also allow multipole genomic interpretations: 3 clinical relevant variants and
    # 5 genetic side variants. Therefore, we could allow a compound heterozygous patient
    # to be captured with both clinical relevant variants

    genomic_interpretation_variant = GenomicInterpretation(
        subject_or_biosample_id=phenopacket_id,
        interpretation_status=interpretation_status,
        variant_interpretation=variant_interpretation
    )

    # TODO(frehburg, grafea) - (1) - I believe we should only keep the genomic
    #  interpretation with the variant data (above).
    #  In this setting, where we have short variants (single nucleotide polymorphisms
    #  (SNP) or short insertions/deletions),
    #  we can infer the gene from the variant data. In general, the `gene` field of
    #  the GenomicInterpretation should
    #  be used if we do not have the variant data, for instance, to represent the
    #  candidate
    #  or the most likely causal gene.
    # genomic_interpretation_gene = GenomicInterpretation(
    #     subject_or_biosample_id=phenopacket_id,
    #     interpretation_status=interpretation_status,
    #     gene=gene
    # )

    diagnosis = Diagnosis(
        # TODO(frehburg, grafea) - (2) - if we are including the diagnosis in the
        #  phenopacket, then we must add
        #  the `disease` field - a required field of the Diagnosis element.
        #  The disease is an ontology class, so we need an
        #  id (e.g. `MONDO:0019115`) and a label (e.g. `obesity due to melanocortin 4
        #  receptor deficiency`)
        #  as in http://purl.obolibrary.org/obo/MONDO_0019115.
        #  Adam, Filip, please select the disease code!

        # so we can add ontologyClass: id: "ORPHA:71529", 
        # label: "Obesity due to melanocortin 4 receptor deficiency"
        genomic_interpretations=[
            # TODO(frehburg, grafea) - (3) - please delete the comment and the line
            #  below if you agree with dropping
            #  the gene interpretation.
            # genomic_interpretation_gene,
            genomic_interpretation_variant,
        ],
        disease=disease,
    )

    interpretation_id = uuid.uuid4()
    interpretation = Interpretation(
        id=str(interpretation_id),
        # Generates a random str like `4d062c1e-ea58-4ad9-8307-b7d07fe6b0ab`
        # consider setting `progress_status`
        #  https://phenopacket-schema.readthedocs.io/en/latest/interpretation.html
        #  #progressstatus
        #  Right now it is set to the default value = `UNKNOWN_PROGRESS`.
        #  However, we *do* have the diagnosis, which is inconsistent with the
        #  unknown progress.
        #  I think this is a clinical question. Adam, can we consider the variants as
        #  causal/contributory
        #  (per https://phenopacket-schema.readthedocs.io/en/latest/genomic
        #  -interpretation.html#interpretationstatus)
        #  to the disease? If yes, then we can make the diagnosis and set the
        #  progress status, right?

        # we can switch the default value of progress_status to 'SOLVED', as all 
        # diseases are definitive diagnoses. 
        # the variants can be considered as 'contributory' 
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
    logger.trace(f'Mapping gene descriptor with the following parameters:'
                 f'\n\thgnc: {hgnc}'
                 f'\n\tsymbol: {symbol}'
                 f'\n\tomims: {omims}'
                 f'\n\tno_omim: {no_omim}')

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


def _map_disease_for_diagnosis(
        orpha: str,
        label: str,
) -> OntologyClass:
    """Maps ERKER patient data to Disease block

    Phenopackets Documentation of the Diagnosis block:
    https://phenopacket-schema.readthedocs.io/en/latest/interpretation.html#rstdiagnosis

    :param orpha: Orpha code encoding rare disease
    :type orpha: str
    :param label: human-readable class name
    :type label: str
    :return: OntologyClass Phenopackets block of disease
    """
    logger.trace(f'Mapping disease with the following parameters:'
                 f'\n\torpha: {orpha}'
                 f'\n\tlabel: {label}'
                 )

    disease = OntologyClass(
        id=orpha,
        label=label
    )

    return disease


def _map_disease_block(
        orpha: str,
        date_of_diagnosis: str,
        label: str,
        no_date: str,
) -> OntologyClass:
    """Maps ERKER patient data to Disease block

    Phenopackets Documentation of the Disease block:
    https://phenopacket-schema.readthedocs.io/en/latest/disease.html#rstdisease

    :param orpha: Orpha code encoding rare disease
    :type orpha: str
    :param date_of_diagnosis: date of diagnosis
    :type date_of_diagnosis: str
    :param label: human-readable class name
    :type label: str
    :param no_date: symbol for missing date
    :type no_date: str
    :return: Disease Phenopackets block
    """
    logger.trace(f'Mapping disease with the following parameters:'
                 f'\n\torpha: {orpha}'
                 f'\n\tdate_of_diagnosis: {date_of_diagnosis}'
                 f'\n\tlabel: {label}'
                 f'\n\tno_date: {no_date}'
                 )

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
    logger.trace('Called _get_constants_from_config()')
    no_mutation = config.get('NoValue', 'mutation')
    no_phenotype = config.get('NoValue', 'phenotype')
    no_date = config.get('NoValue', 'date')
    no_omim = config.get('NoValue', 'omim')
    not_recorded = config.get('NoValue', 'recorded')

    created_by = config.get('Constants', 'creator_tag')

    logger.trace('Successfully finished _get_constants_from_config()')

    return no_mutation, no_phenotype, no_date, no_omim, not_recorded, created_by
