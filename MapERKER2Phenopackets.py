from phenopackets import Individual, PhenotypicFeature, OntologyClass, Phenopacket
from phenopackets import Measurement
from phenopackets import Disease
from phenopackets import Interpretation
from phenopackets import MetaData
from phenopackets import VariantInterpretation
from phenopackets import Resource
from google.protobuf.internal.well_known_types import Timestamp

from ParseErker import parse_erker_date_of_birth, parse_erker_sex


def create_resource(id: str, name: str, namespace_prefix: str, url: str, version: str, iri_prefix: str) -> Resource:
    """A convenience method to create a Phenopacket Schema resource.

    :param id: The id of the resource.
    :type id: str
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
        id=id, name=name, namespace_prefix=namespace_prefix,
        url=url, version=version, iri_prefix=iri_prefix
    )


def map_erker2phenopackets(df):
    ERKER_phenopackets = []
    # vorher quasi nur mapping, hier zusammensetzen
    for i, (idx, row) in enumerate(df.iterrows()):
        ## Subject
        # The elements we may consider adding:
        #  age at last encounter, vital status, karyotypic sex, gender

        subject = Individual(
            id=str(idx),
            date_of_birth=parse_erker_date_of_birth(row['sct_184099003_y']),
            sex=parse_erker_sex(row['sct_281053000']),
            taxonomy=OntologyClass(id='NCBITaxon:9606', label='Homo sapiens')
        )

        ## PhenotypicFeatures
        # Unsure if it is useful to add HPO terms in this dataset,
        #  considering we have the weight measurements.
        phenotypicFeatures = PhenotypicFeature(
            type=OntologyClass(id='HP:0001513', label='Obesity')

        )
        ## Measurements
        # TODO - the weight course
        measurements = Measurement(

        )

        ## Interpretations
        interpretation = Interpretation(
            id=str(idx),
            progress_status='SOLVED',
            # diagnosis=Diagnosis(id='ORPHA:71529', label='Obesity due to melanocortin 4 receptor deficiency'),
        )

        # TODO - add variants
        variantInterpretation = VariantInterpretation(
            acmg_pathogenicity_classification='NOT_PROVIDED',  # acmg will be added
            therapeutic_actionability='UNKNOWN_ACTIONABILITY',
            #  variant=parse_erker_hgvs()

        )

        ## Disease
        disease = Disease(
            term=OntologyClass(id='ORPHA:71529', label='Obesity due to melanocortin 4 receptor deficiency'),
            #    onset=parse_erker_onset(row['sct_424850005']),
        )

        ## MetaData
        created = Timestamp()
        created.GetCurrentTime()

        resources = [
            create_resource('ncbitaxon', 'NCBI organismal classification', 'NCBITaxon',
                            'http://purl.obolibrary.org/obo/ncbitaxon.owl', '2021-06-10',
                            'http://purl.obolibrary.org/obo/NCBITaxon_')
        ]

        meta_data = MetaData(
            created=created,
            created_by=created_by,
            submitted_by=created_by,  # The same for simplicity
            resources=resources,
            phenopacket_schema_version=phenopacket_schema_version
        )

        pp = Phenopacket(
            id=f'{i}-{idx}',  # TODO - can we come up with a better ID?
            subject=subject,
            phenotypic_features=[phenotypicFeatures],
            interpretations=[interpretation],
            meta_data=meta_data,
            measurements=[],

        )
        ERKER_phenopackets.append(pp)

    print(f'Mapped {len(ERKER_phenopackets)} phenopackets')
