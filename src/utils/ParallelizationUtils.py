from typing import List

import polars as pl


def calc_chunk_size(num_instance: int, num_chunks: int) -> List[int]:
    """
    Calculate chunk sizes for even workload distribution.
    :param num_instance: Number of instances or rows
    :type num_instance: int
    :param num_chunks: Number of chunks
    :type num_chunks: int
    :return: List of chunk sizes
    :rtype: List[int]
    :raises ValueError: If num_chunks or num_instance is 0
    """
    if num_chunks == 0 or num_instance == 0:
        raise ValueError("num_chunks and num_instance must be greater than 0")

    chunk_size = num_instance // num_chunks
    remainder = num_instance % num_chunks

    # remainder is necessarily smaller than num_chunks
    # therefore, we can just add 1 to the first remainder number of chunks
    chunk_sizes = [
        chunk_size + 1 if i < remainder else chunk_size for i in range(num_chunks)
    ]
    return chunk_sizes


def split_dataframe(df: pl.DataFrame, chunk_sizes: List[int]) -> List:
    """
    Split DataFrame into chunks.
    :param chunk_sizes: List of chunk sizes
    :type chunk_sizes: List[int]
    :param df: DataFrame
    :type df: pd.DataFrame
    :return: List of DataFrames
    :rtype: List[pd.DataFrame]
    """
    return []


if __name__ == "__main__":
    df = pl.DataFrame(
        {
            "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "b": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "c": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        }
    )
    # chunk_sizes = calc_chunk_size(num_instance=df.height, num_chunks=3)
    # for df_sub in split_dataframe(df, chunk_sizes):
    #     print(df_sub.height)
    df_sub = df.slice(0, 20)
    print(f'height: {df_sub.height}, type: {type(df_sub)}')