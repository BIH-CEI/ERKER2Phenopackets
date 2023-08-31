from typing import List

import polars as pl


def remove_all_null_cols(df: pl.DataFrame) -> pl.DataFrame:
    """
    Remove all columns that have only null values
    :param df: DataFrame with columns with only null values
    :type df: pl.DataFrame
    :return:  without only null columns
    :rtype: pl.DataFrame
    """
    all_null_cols = get_all_null_cols(df)
    return df.drop(all_null_cols)


def get_all_null_cols(df: pl.DataFrame) -> List[str]:
    """
    Get names of all columns that have only null values
    :param df: DataFrame with columns with only null values
    :type df: pl.DataFrame
    :return: List of column names with only null values
    :rtype: List[str]
    """
    return df.select(
        pl.all()
        .is_null()
        .all()
    ).melt().filter(
        pl.col('value')  # == True
    ).select('variable').to_series().to_list()


def count_all_null_cols(df: pl.DataFrame) -> int:
    """
    Get number of columns that have only null values
    :param df: DataFrame with columns with only null values
    :type df: pl.DataFrame
    :return: number of columns with only null values
    :rtype: int
    """
    return len(get_all_null_cols(df))


def get_num_cols(df: pl.DataFrame) -> int:
    """
    Get number of columns in DataFrame
    :param df: DataFrame
    :type df: pl.DataFrame
    :return: number of columns
    :rtype: int
    """
    return df.shape[1]


def get_num_rows(df: pl.DataFrame) -> int:
    """
    Get number of rows in DataFrame
    :param df: DataFrame
    :return: number of rows
    :rtype: int
    """
    return df.shape[0]
