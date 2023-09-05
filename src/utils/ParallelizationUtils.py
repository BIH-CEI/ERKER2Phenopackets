from typing import List


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
