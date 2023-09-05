from typing import List


def calc_chunk_size(num_instance: int, num_chunks: int) -> List[int]:
    """
    Calculate chunk sizes for even workload distribution.
    :param num_instance: Number of instances or rows
    :type num_instance: int
    :param num_chunks: Number of chunks
    :type num_chunks: int
    :return: List of chunk sizes
    """
    chunk_size = num_instance // num_chunks
    remainder = num_instance % num_chunks
    chunk_sizes = [chunk_size] * num_chunks

    return []