from typing import List

import pandas as pd
import phenopackets
from phenopackets import Individual, PhenotypicFeature, OntologyClass, Phenopacket
from phenopackets import Measurement
from phenopackets import Disease
from phenopackets import Interpretation
from phenopackets import MetaData
from phenopackets import VariantInterpretation
from phenopackets import Resource
from google.protobuf.internal.well_known_types import Timestamp

from ParseErker import parse_erker_date_of_birth, parse_erker_sex


def map_erker2phenopackets(df: pd.DataFrame, created_by: str):
    erker_phenopackets = []
    # vorher quasi nur mapping, hier zusammensetzen
    resources = [
        create_resource('ncbitaxon', 'NCBI organismal classification', 'NCBITaxon',
                        'http://purl.obolibrary.org/obo/ncbitaxon.owl', '2021-06-10',
                        'http://purl.obolibrary.org/obo/NCBITaxon_')
    ]

    for i, (phenopacket_id, row) in enumerate(df.iterrows()):
        phenopacket_id = f'{i}-{phenopacket_id}'  # TODO: can we come up with a better ID?
        phenopacket = map_erker_row2phenopacket(phenopacket_id, row, resources, created_by)
        erker_phenopackets.append(phenopacket)

    print(f'Mapped {len(erker_phenopackets)} phenopackets')
    return erker_phenopackets


def create_measurements():
    """[WIP]Creates a measurement object for a phenopacket.
    Currently not implemented
    """
    ## Measurements
    # TODO - the weight course
    measurement = Measurement(

    )
    return None


def map_erker_row2phenopacket(
        phenopacket_id: str, row: pd.Series,
        resources: List[Resource], created_by: str, phenopacket_schema_version=phenopackets.__version__
):
    subject = create_subject(phenopacket_id, row)

    # TODO: this does not require any patient specific data, maybe move it out of the loop
    phenotypic_features = create_phenotypic_features()

    measurements = create_measurements()

    interpretation = create_interpretation(phenopacket_id)

    # TODO - add variants
    variantInterpretation = VariantInterpretation(
        acmg_pathogenicity_classification='NOT_PROVIDED',  # TODO: acmg will be added
        therapeutic_actionability='UNKNOWN_ACTIONABILITY',
        #  variant=parse_erker_hgvs()

    )  # TODO: this is not used in the phenopacket definition below

    ## Disease
    disease = Disease(
        term=OntologyClass(id='ORPHA:71529', label='Obesity due to melanocortin 4 receptor deficiency'),
        #    onset=parse_erker_onset(row['sct_424850005']),
    )  # TODO: this is not used in the phenopacket definition below

    ## MetaData
    created = Timestamp()
    created.GetCurrentTime()

    meta_data = MetaData(
        created=created,
        created_by=created_by,
        submitted_by=created_by,  # The same for simplicity
        resources=resources,
        phenopacket_schema_version=phenopacket_schema_version
    )

    phenopacket = Phenopacket(
        id=phenopacket_id,  # TODO: is this a valid id here?
        subject=subject,
        phenotypic_features=[phenotypic_features],
        interpretations=[interpretation],
        meta_data=meta_data,
        measurements=[],

    )
    return phenopacket


def create_resource(phenopacket_id: str, name: str, namespace_prefix: str, url: str, version: str,
                    iri_prefix: str) -> Resource:
    """A convenience method to create a Phenopacket Schema resource.

    :param phenopacket_id: The id of the resource.
    :type phenopacket_id: str
    :param name: The name of the resource.
    :type name: str
    :param namespace_prefix: The namespace prefix of the resource.
    :type namespace_prefix: str
    :param url: The url of the resource.
    :type url: str
    :param version: The version of the resource.
    :type version: str
    :param iri_prefix: The iri prefix of the resource.
    :type iri_prefix: str
    :return: A Phenopacket Schema Resource object.
    :rtype: Resource
    """
    return Resource(
        id=phenopacket_id,  # The id of the resource is not the same as the id of the phenopacket.
        name=name, namespace_prefix=namespace_prefix,
        url=url, version=version, iri_prefix=iri_prefix
    )


def create_subject(phenopacket_id: str, row: pd.Series) -> Individual:
    """Creates the Individual block of a Phenopacket.

    :param phenopacket_id: The id of the phenopacket.
    :type phenopacket_id: str
    :param row: The row of the Erker dataset.
    :type row: pd.Series
    :return: A Phenopacket Schema Individual object.
    :rtype: Individual
    """
    # TODO: The elements we may consider adding:
    #  age at last encounter, vital status, karyotypic sex, gender
    subject = Individual(
        id=phenopacket_id,  # TODO: is this a valid id here?
        date_of_birth=parse_erker_date_of_birth(row['sct_184099003_y']),
        sex=parse_erker_sex(row['sct_281053000']),
        taxonomy=OntologyClass(id='NCBITaxon:9606', label='Homo sapiens')
    )

    return subject


def create_phenotypic_features():
    """Creates the PhenotypicFeatures block of a Phenopacket.

    :return: List of phenotypic features
    :rtype: List[PhenotypicFeatures]
    """
    # TODO: Unsure if it is useful to add HPO terms in this dataset,
    #  considering we have the weight measurements.
    # TODO: Currently hard coded
    phenotypic_features = PhenotypicFeature(
        type=OntologyClass(id='HP:0001513', label='Obesity')

    )
    return [phenotypic_features]


def create_interpretation(phenopacket_id: str) -> Interpretation:
    """Creates an interpretation object for a phenopacket.

    :param phenopacket_id: The id of the phenopacket.
    :type phenopacket_id: str
    """
    interpretation = Interpretation(
        id=phenopacket_id,  # TODO: is this a valid id here?
        progress_status='SOLVED',
        # diagnosis=Diagnosis(phenopacket_id='ORPHA:71529', label='Obesity due to melanocortin 4 receptor deficiency'),
    )
    return interpretation