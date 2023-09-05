import os
from typing import List

import polars as pl
from phenopackets import Phenopacket

from src.utils.ParallelizationUtils import calc_chunk_size


def map_mc4r2phenopackets(df: pl.DataFrame, created_by: str) -> List[Phenopacket]:
    """
    Map MC4R DataFrame to List of Phenopackets.

    Maps the MC4R DataFrame to a list of Phenopackets. Each row in the DataFrame
    represents a single Phenopacket. The Phenopacket.id is the index of the row.
    Uses parallel processing to speed up the mapping.

    :param df: MC4R DataFrame
    :type df: pl.DataFrame
    :param created_by: Name of creator
    :type created_by: str
    :return: List of Phenopackets
    :rtype: List[Phenopacket]
    """
    # divide the DataFrame into chunks
    num_threads = os.cpu_count()
    chunk_sizes = calc_chunk_size(num_chunks=num_threads, num_instances=df.height)


    return []


def _map_chunk():
    pass



