from typing import List, Union, Dict, Any, Callable, Type, Tuple
import warnings

import numpy as np
import polars as pl
from loguru import logger
from matplotlib import pyplot as plt


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
    logger.info(f'There are {count_all_null_cols(df)}/{df.width} columns with only '
                f'null '
                f'values in the data')
    logger.info(f'There are {at_least_1_null}/{df.width} columns with at least one null'
                f' value in the data')

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

    logger.info(f'Dropped {num_cols_start - num_cols_end} columns. {num_cols_end} '
                'columns remaining.')
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
               id_prefix: str = None, id_suffix: str = None, id_datatype: Type = int
               ) -> pl.DataFrame:
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
    :param id_datatype: the datatype of the id column, if id_suffix and id_prefix are
        not specified
    :type id_datatype: Type
    :return: DataFrame with id column
    :rtype: pl.DataFrame
    """
    if not id_prefix and not id_suffix:
        if id_datatype == int:
            df = df.with_columns((pl.Series(range(0, df.height))).alias(id_col_name))
        elif id_datatype == str:
            ids = [str(i) for i in range(0, df.height)]
            df = df.with_columns((pl.Series(ids)).alias(id_col_name))
        else:
            raise ValueError(f'id_datatype has to be int or str, not {id_datatype}')
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
        map_from: Union[str, List[str]], map_to: str,
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


    When mapping multiple columns with a function, the function should not take
    positional or keyword arguments, but use `args`. The contents of args can the be
    used to access the values of the columns to be mapped. Make sure to pass the
    columns in the correct order.

    Example:
    ```def map_func(*args):
        return 2*args[0] + args[1] / args[2]```

    :param df: The dataframe
    :type df: pl.DataFrame
    :param map_from: the name or names of the column(s) to map from (in correct order)
    :type map_from: str
    :param map_to: name of the new column to be created as a result of the mapping
    :type map_to: str
    :param mapping: a dictionary or function to mapping with
    :type mapping: Union[Dict[Any, Any], Callable[[...], Any]]
    :param default: the default value to use if no match is found in the dictionary
    :type default: Any
    :return: the dataframe with the new column
    :rtype: pl.DataFrame
    :raises: ValueError: if map_from is a list and mapping is a dictionary
    """
    if isinstance(mapping, dict):
        if isinstance(map_from, list):  # multiple columns
            raise ValueError('When mapping with a dictionary, map_from must be a '
                             'single column and not a list of columns.')
        return _map_col_dict(df=df,
                             col_name=map_from, new_col_name=map_to,
                             dictionary=mapping, default=default
                             )
    elif callable(mapping):
        if default:
            warnings.warn('Default value is ignored when using a function to mapping')
        if isinstance(map_from, str):  # one column
            return _map_col_function(df=df,
                                     col_name=map_from, new_col_name=map_to,
                                     function=mapping
                                     )
        elif isinstance(map_from, list):  # multiple columns
            return _map_cols_function(df=df,
                                      col_names=map_from, new_col_name=map_to,
                                      function=mapping
                                      )


def _map_col_dict(df: pl.DataFrame,
                  col_name: str, new_col_name: str,
                  dictionary: Dict[Any, Any], default: Any = None) -> pl.DataFrame:
    """
    Map values in column to new values using dictionary

    Helper function for map_col

    :param df: The dataframe
    :type df: pl.DataFrame
    :param col_name: the name of the column to map from
    :type col_name: str
    :param new_col_name: name of the new column to be created as a result of the mapping
    :type new_col_name: str
    :param dictionary: a dictionary to mapping with
    :type dictionary: Dict[Any, Any]
    :param default: the default value to use if no match is found in the dictionary
    :type default: Any
    :return: the dataframe with the new column
    :rtype: pl.DataFrame
    """
    return df.with_columns(
        pl.col(col_name).map_dict(dictionary, default=default).alias(new_col_name)
    )


def _map_col_function(df: pl.DataFrame,
                      col_name: str, new_col_name: str,
                      function: Callable[[...], Any]) -> pl.DataFrame:
    """
    Map values in column to new values using function

    Helper function for map_col

    :param df: The dataframe
    :type df: pl.DataFrame
    :param col_name: the name of the column to map from
    :type col_name: str
    :param new_col_name: name of the new column to be created as a result of the mapping
    :type new_col_name: str
    :param function: a function to mapping with
    :type function: Callable[[...], Any]
    :return: the dataframe with the new column
    :rtype: pl.DataFrame
    """
    return df.with_columns(
        pl.col(col_name).apply(function).alias(new_col_name)
    )


def _map_cols_function(df: pl.DataFrame,
                       col_names: List[str], new_col_name: str,
                       function: Callable[[...], Any]) -> pl.DataFrame:
    """
    Map values in multiple columns to new values using function

    Helper function for map_col

    :param df: The dataframe
    :type df: pl.DataFrame
    :param col_names: the names of the columns to map from
    :type col_names: List[str]
    :param new_col_name: name of the new column to be created as a result of the mapping
    :type new_col_name: str
    :param function: a function to mapping with
    :type function: Callable[[...], Any]
    :return: the dataframe with the new column
    :rtype: pl.DataFrame
    """
    return df.with_columns(
        pl.struct(col_names).apply(function).alias(new_col_name)
    )


def fill_null_vals(df: pl.DataFrame, col: str, value: Any) -> pl.DataFrame:
    """
    Fill null values in column with value
    :param df: DataFrame with null values
    :type df: pl.DataFrame
    :param col: Name of column with null values
    :type col: str
    :param value: Any value to fill the null values in the column
    :type value: Any
    :return: Dataframe with filled null values
    :rtype: pl.DataFrame
    """
    return df.with_columns(
        pl.col(col).fill_null(value=value)
    )


def contingency_table(df, col1_name, col2_name):
    """
    Create a contingency table (np array) of two columns
    :param df: the dataframe
    :param col1_name: the name of the first column
    :param col2_name: the name of the second column
    :return: a contingency table of two columns
    """
    num_col1 = df[col1_name].n_unique()
    num_col2 = df[col2_name].n_unique()

    grouped_by_both = df.groupby([col1_name, col2_name]).count()

    c_table = np.zeros((num_col1, num_col2))

    for i, z in enumerate(df[col1_name].unique()):
        for j, c in enumerate(df[col2_name].unique()):
            result = (grouped_by_both
                      .filter(
                (grouped_by_both[col1_name] == z)
                & (grouped_by_both[col2_name] == c))
                      .select(['count']))
            if not result.is_empty():
                c_table[i, j] = result['count'][0]
    return c_table


def barchart_3d(df: pl.DataFrame,
                col1_name: str, col2_name: str,
                figsize: Tuple[int, int],
                grouped_by_col1: pl.DataFrame = None,
                grouped_by_col2: pl.DataFrame = None
                ):
    """
    Create a 3D barchart of the contingency table of two columns

    :param df: the dataframe
    :param col1_name: the name of the first column
    :param col2_name: the name of the second column
    :param figsize: a tuple of the figure size e.g. (10, 10)
    :param grouped_by_col1: a dataframe grouped by the first column with count e.g.,
        df.groupby(col1_name).count()
    :param grouped_by_col2: a dataframe grouped by the second column with count
    """
    if grouped_by_col1 is None:
        grouped_by_col1 = df.groupby(col1_name).count()
    if grouped_by_col2 is None:
        grouped_by_col2 = df.groupby(col2_name).count()
    col1_labels = grouped_by_col1[col1_name]
    col2_labels = grouped_by_col2[col2_name]
    ct = contingency_table(df, col1_name, col2_name)

    num_col1 = df[col1_name].n_unique()
    num_col2 = df[col2_name].n_unique()

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')

    xpos, ypos = np.meshgrid(np.arange(num_col1), np.arange(num_col2))
    xpos = xpos.flatten()
    ypos = ypos.flatten()
    zpos = np.zeros_like(xpos)

    dx = dy = 0.5
    dz = np.array(ct).flatten()

    ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color='b')

    ax.set_xticks(np.arange(num_col1))
    ax.set_xticklabels(col1_labels)
    ax.set_yticks(np.arange(num_col2))
    ax.set_yticklabels(col2_labels)

    ax.set_xlabel(col1_name)
    ax.set_ylabel(col2_name)
    ax.set_zlabel('Count')

    plt.show()


def barchart_subplot(ax, x, y, title='', x_label='', y_label='', color='',
                     x_tick_rotation='horizontal'):
    if color == '':
        ax.bar(x, y)
    else:
        ax.bar(x, y, color=color)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xticks(x)
    ax.set_xticklabels(x, rotation=x_tick_rotation)
    ax.set_axisbelow(True)


def barchart(x, y, title='', x_label='', y_label='', color='',
             x_tick_rotation='horizontal', figsize=(20, 15)):
    plt.figure(figsize=figsize)
    if color == '':
        plt.bar(x, y)
    else:
        plt.bar(x, y, color=color)
    plt.xticks(rotation=x_tick_rotation)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()


def piechart_subplot(ax, labels, sizes, title='', colors=None, startangle=140,
                     autopct='%1.1f%%', legend_loc='upper right'):
    if colors is None:
        ax.pie(sizes, labels=labels, autopct=autopct, startangle=startangle)
    else:
        ax.pie(sizes, labels=labels, autopct=autopct, startangle=startangle,
               colors=colors)
    ax.set_title(title)
    ax.axis('equal')
    ax.legend(labels, loc=legend_loc, bbox_to_anchor=(1, 0.9))


def piechart(labels, sizes, title='', colors=None, startangle=140,
                     autopct='%1.1f%%', legend_loc='upper right', figsize=(20, 15)):
    plt.figure(figsize=figsize)
    if colors is None:
        plt.pie(sizes, labels=labels, autopct=autopct, startangle=startangle)
    else:
        plt.pie(sizes, labels=labels, autopct=autopct, startangle=startangle,
               colors=colors)
    plt.title(title)
    plt.axis('equal')
    plt.legend(labels, loc=legend_loc, bbox_to_anchor=(1, 0.9))

    plt.show()


def barchart_relative_distribution(x, y, title='', x_label='', color='',
                                   x_tick_rotation='vertical', figsize=(20, 10)):
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()

    if color == '':
        ax1.bar(x, y)
    else:
        ax1.bar(x, y, color=color)
    ax1.set_ylabel('Counts', color='blue')

    rel_freq = y / sum(y)
    ax2.plot(x, rel_freq, linestyle='-', marker='o', color='red')
    ax2.set_ylabel('Relative Distribution', color='red')

    ax1.set_xticks(x)
    ax1.set_xticklabels(x, rotation=x_tick_rotation)
    plt.title(title)
    ax1.set_xlabel(x_label)
    plt.show()