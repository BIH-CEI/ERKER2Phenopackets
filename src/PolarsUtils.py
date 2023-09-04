from typing import List, Union, Dict, Any, Callable
import warnings

import polars as pl


def null_value_analysis(df: pl.DataFrame, verbose=False) -> Union[None, pl.DataFrame]:
    """This method prints an analysis of null values in a DataFrame
    :param df: DataFrame to analyze
    :type df: pl.DataFrame
    :param verbose: If true, method returns DataFrame with null value analysis
    :type verbose: bool
    """
    null_analysis = df.select(
        pl.all().is_null().sum()
    ).melt().filter(
        pl.col('value') > 0
    ).rename({'value': 'null_count'})

    null_analysis = null_analysis.with_columns(
        (pl.col('null_count') == get_num_rows(df)).alias('all_null')
    )

    at_least_1_null = null_analysis.filter(0 < null_analysis['null_count']).height
    print(f'There are {count_all_null_cols(df)}/{df.width} columns with only null '
          f'values in the data')
    print(f'There are {at_least_1_null}/{df.width} columns with at least one null '
          f'value in the data')

    if verbose:
        return null_analysis


def drop_null_cols(df: pl.DataFrame, remove_all_null: bool, remove_any_null: bool) -> \
        pl.DataFrame:
    """
    Remove all columns that have only null values
    :param df: DataFrame with columns with only null values
    :type df: pl.DataFrame
    :param remove_all_null: If True, remove columns with only null values.
    :type remove_all_null: bool
    :param remove_any_null: If True, remove columns with any null values
    :type remove_any_null: bool
    :return:  without only null columns
    :rtype: pl.DataFrame
    """
    num_cols_start = df.width
    if remove_all_null:
        all_null_cols = get_all_null_cols(df)
        df = df.drop(all_null_cols)
    if remove_any_null:
        any_null_cols = get_any_null_cols(df)
        df = df.drop(any_null_cols)

    num_cols_end = df.width

    print(f'Dropped {num_cols_start - num_cols_end} columns. {num_cols_end} columns '
          f'remaining.')
    return df


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


def get_any_null_cols(df: pl.DataFrame) -> List[str]:
    """
    Get names of all columns that have any null values
    :param df: DataFrame with columns with any null values
    :type df: pl.DataFrame
    :return: List of column names with any null values
    :rtype: List[str]
    """
    return df.select(
        pl.all()
        .is_null()
        .any()
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
    return df.height


def get_num_rows(df: pl.DataFrame) -> int:
    """
    Get number of rows in DataFrame
    :param df: DataFrame
    :return: number of rows
    :rtype: int
    """
    return df.width


def add_id_col(df: pl.DataFrame,
               id_col_name: str,
               id_prefix: str = None, id_suffix: str = None) -> \
        pl.DataFrame:
    """
    Add id column to DataFrame

    Example usage:
    id_prefix = 'row_'
    id_suffix = '_id'
    id_col = 'row_{i}_id' for i in range(0, df.height)

    :param df: DataFrame
    :type df: pl.DataFrame
    :param id_col_name: Name of id column
    :type id_col_name: str
    :param id_prefix: Prefix for id column
    :type id_prefix: str
    :param id_suffix: Suffix for id column
    :type id_suffix: str
    :return: DataFrame with id column
    :rtype: pl.DataFrame
    """
    # add id column with prefix and/or suffix
    if not id_prefix and not id_suffix:
        df = df.with_columns((pl.Series(range(0, df.height))).alias(id_col_name))
    elif id_prefix and not id_suffix:
        df = df.with_columns((pl.Series(
            f'{id_prefix}{i}' for i in range(0, df.height)
        )).alias(id_col_name))
    elif not id_prefix and id_suffix:
        df = df.with_columns((pl.Series(
            f'{i}{id_suffix}' for i in range(0, df.height)
        )).alias(id_col_name))
    else:
        df = df.with_columns((pl.Series(
            f'{id_prefix}{i}{id_suffix}' for i in range(0, df.height)
        )).alias(id_col_name))

    # move id column to front
    order = [id_col_name] + [col for col in df.columns if col != id_col_name]
    return df.select(order)


def map_col(
        df: pl.DataFrame,
        col_name: str, new_col_name: str,
        mapping: Union[Dict[Any, Any], Callable[[...], Any]],
        default: Any = None) -> pl.DataFrame:
    """
    Map values in column to new values using dictionary or mapping function

    When mapping with a function, the function should only take a single positional
    argument and return a single value. The function should not have any side effects.

    Avoid mapping with a function if possible, as it is much slower than mapping with a
    dictionary. Therefore, avoid using functions as shown below.

    ```def map_func(x):
        return dictionary[x]```

    :param df: The dataframe
    :type df: pl.DataFrame
    :param col_name: the column to mapping from
    :type col_name: str
    :param new_col_name: the column to mapping to
    :type new_col_name: str
    :param mapping: a dictionary or function to mapping with
    :type mapping: Union[Dict[Any, Any], Callable[[...], Any]]
    :param default: the default value to use if no match is found in the dictionary
    :type default: Any
    :return: the dataframe with the new column
    :rtype: pl.DataFrame
    """
    if type(mapping) == dict:
        return _map_col_dict(df=df,
                             col_name=col_name, new_col_name=new_col_name,
                             dictionary=mapping, default=default
                             )
    elif callable(mapping):
        if default:
            warnings.warn('Default value is ignored when using a function to mapping')
        return _map_col_function(df=df,
                                 col_name=col_name, new_col_name=new_col_name,
                                 function=mapping
                                 )


def _map_col_dict(df: pl.DataFrame,
                  col_name: str, new_col_name: str,
                  dictionary: Dict[Any, Any], default: Any = None) -> pl.DataFrame:
    return df.with_columns(
        pl.col(col_name).map_dict(dictionary, default=default).alias(new_col_name)
    )


def _map_col_function(df: pl.DataFrame,
                      col_name: str, new_col_name: str,
                      function: Callable[[...], Any]) -> pl.DataFrame:
    print(type(function))
    return df.with_columns(
        pl.col(col_name).apply(function).alias(new_col_name)
    )