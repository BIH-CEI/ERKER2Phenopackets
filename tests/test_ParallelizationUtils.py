import pytest

from src.utils.ParallelizationUtils import calc_chunk_size


@pytest.mark.parametrize(
    ('num_instances', 'num_chunks', 'expected'),
    (
        (16, 3, [6, 5, 5]),
        (16, 4, [4, 4, 4, 4]),
        (16, 5, [4, 3, 3, 3, 3]),
        (129, 2, [65, 64]),
    )
)
def test_calc_chunk_size(num_instances, num_chunks, expected):
    result = calc_chunk_size(num_instances, num_chunks)
    assert result == expected
    assert sum(result) == num_instances


@pytest.mark.parametrize(
    ('num_instances', 'num_chunks', 'expected'),
    (
            (0, 3, []),
            (3, 0, []),
    )
)
def test_calc_chunk_size_invalid_params(num_instances, num_chunks, expected):
    with pytest.raises(ValueError):
        calc_chunk_size(num_instances, num_chunks)
