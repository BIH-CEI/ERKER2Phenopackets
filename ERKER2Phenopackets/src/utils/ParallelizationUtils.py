from typing import List

import polars as pl


def calc_chunk_size(num_instances: int, num_chunks: int) -> List[int]:
    """
    Calculate chunk sizes for even workload distribution.
    :param num_instances: Number of instances or rows
    :type num_instances: int
    :param num_chunks: Number of chunks
    :type num_chunks: int
    :return: List of chunk sizes
    :rtype: List[int]
    :raises ValueError: If num_chunks or num_instance is 0
    """
    if num_chunks == 0 or num_instances == 0:
        raise ValueError("num_chunks and num_instances must be greater than 0")

    chunk_size = num_instances // num_chunks
    remainder = num_instances % num_chunks

    # remainder is necessarily smaller than num_chunks
    # therefore, we can just add 1 to the first remainder number of chunks
    chunk_sizes = [
        chunk_size + 1 if i < remainder else chunk_size for i in range(num_chunks)
    ]
    return chunk_sizes


def split_dataframe(df: pl.DataFrame, chunk_sizes: List[int]) -> List[pl.DataFrame]:
    """
    Split DataFrame into chunks.
    :param chunk_sizes: List of chunk sizes
    :type chunk_sizes: List[int]
    :param df: DataFrame
    :type df: pd.DataFrame
    :return: List of DataFrames
    :rtype: List[pd.DataFrame]
    :raises ValueError: If chunk_sizes is None or empty
    """
    if chunk_sizes is None or len(chunk_sizes) == 0:
        raise ValueError("chunk_sizes must not be None or empty")
    if len(chunk_sizes) == 1:
        return [df]
    chunk_intervals = [
        (sum(chunk_sizes[:i]), chunk_sizes[i])
        for i in range(len(chunk_sizes))
    ]
    return [df.slice(start, length) for (start, length) in chunk_intervals]
