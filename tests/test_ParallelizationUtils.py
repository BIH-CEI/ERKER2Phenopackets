import pytest
import polars as pl

from src.utils.ParallelizationUtils import calc_chunk_size, split_dataframe


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


@pytest.mark.parametrize(
    ('df', 'num_chunks'),
    (
            (
                pl.DataFrame(
                    {
                        "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        "b": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                        "c": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    }
                ),
                3
            ),
            (
                pl.DataFrame(
                    {
                        "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                        "b": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                        "c": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    }
                ),
                4
            ),
    )
)
def test_split_dataframe(df, num_chunks):
    chunk_sizes = calc_chunk_size(num_instances=df.height, num_chunks=num_chunks)

    for i, df_sub in enumerate(split_dataframe(df, chunk_sizes)):
        assert df_sub.height == chunk_sizes[i]
