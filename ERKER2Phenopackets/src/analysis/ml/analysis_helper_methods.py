from ERKER2Phenopackets.src.utils.graphutils import create_graph, graphplot

from typing import List, Any
from difflib import SequenceMatcher

import polars as pl

from ERKER2Phenopackets.src.utils.polars_utils import melt_groupby_count


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def index_similar(list_: List, value: Any, threshhold: float = 0.95) -> int:
    """Returns the index of the first item in the list that is similar to the value.

    The threshhold defines how similar the items have to be.

    :param list_: a list of items
    :type list_: List
    :param value: an item
    :type value: Any
    :param threshhold: a number between 0 and 1, the higher, the more similar the
    items should be, defaults to 0.95
    :type threshhold: float, optional
    :return: the index of the first item in the list that is similar to the value or
    -1 if no item is similar
    :rtype: int
    """
    for i, item in enumerate(list_):
        if similar(item, value) > threshhold:
            return i
    return -1


def pairs_range(i: int) -> List[List[int]]:
    """
    Creates a range of pairs from [0, 1] to [i-2, i-1]

    :param i: an integer i
    :type i: int
    :return: a list of pairs from [0, 1] to [i-2, i-1]
    :rtype: List[List[int]]
    """
    return [[i, i + 1] for i in range(i - 1)]


def plot_phenotype_transition_graph(
        df: pl.DataFrame,
        label_column_name: str,
        phenotype_labels: List[str],
        initial_counts: List[int],
        count_not_recorded: bool,
        percentages: bool, file_path: str, figsize=None
):
    num_phenotype_labels = len(phenotype_labels)
    num_phenotype_measurements = 5

    counts_dict = {
        i: {
            'total_count': initial_counts[i],
            'counts': [0] * (num_phenotype_labels + 1),
            'frequency': []
        } for i in range(num_phenotype_labels)
    }

    # count transitions
    for row in df.rows(named=True):
        obesity_labels = [row[f'{label_column_name}{i}']
                          for i in range(num_phenotype_measurements)]
        for i0, i1 in pairs_range(num_phenotype_measurements):
            if (  # no source
                    obesity_labels[i0] == 'Not recorded'
                    or
                    obesity_labels[i0] is None
            ):
                continue

            if (  # no target, still count up total
                    obesity_labels[i1] == 'Not recorded'
                    or
                    obesity_labels[i1] is None
            ):
                if count_not_recorded:
                    index0 = index_similar(phenotype_labels, obesity_labels[i0])

                    # + 1 for not recorded
                    counts_dict[index0]['counts'][num_phenotype_labels] += 1
                continue

            index0 = index_similar(phenotype_labels, obesity_labels[i0])
            index1 = index_similar(phenotype_labels, obesity_labels[i1])

            # if the phenotype stays the same, it does not count as a transition
            if obesity_labels[i0] != obesity_labels[i1]:
                counts_dict[index1]['total_count'] += 1
            counts_dict[index0]['counts'][index1] += 1

    if percentages:  # calculate frequencies
        for node in range(num_phenotype_labels):
            if counts_dict[node]['total_count'] == 0:
                counts_dict[node]['frequency'] = [0.0] * num_phenotype_labels
            else:
                counts_dict[node]['frequency'] = [
                    counts_dict[node]['counts'][i] / counts_dict[node]['total_count']
                    for i in range(num_phenotype_labels)]

    # add total counts to node labels
    for node in range(num_phenotype_labels):
        if percentages:
            freq = counts_dict[node]["total_count"] / df.height
            phenotype_labels[node] += f'\n{round(freq * 100, 2)}%'
        else:
            phenotype_labels[node] += \
                f'\n({counts_dict[node]["total_count"]}/{df.height})'

    # create edges
    adjacency_list = [
        [i for i, count in enumerate(counts_dict[node]['counts']) if count > 0] for node
        in range(num_phenotype_labels)]
    if percentages:
        edge_labels = [
            [f'{round(freq * 100, 2)}%' for freq in counts_dict[node]['frequency'] if
             freq > 0.000] for node in range(num_phenotype_labels)]
    else:
        edge_labels = [[f'{count}/{counts_dict[node]["total_count"]}' for count in
                        counts_dict[node]['counts'] if count > 0]
                       for node in range(num_phenotype_labels)]

    G = create_graph(phenotype_labels, edge_labels, adjacency_list, directed=True)
    G.remove_node(num_phenotype_labels)
    print(counts_dict)
    graphplot(G, file_path, layout_prog="dot", orientation="LR", figsize=figsize)


def create_label(*args):
    i = list(args[0].keys())[0][-1]
    hpo = args[0]['obesity_class_hpo' + i]
    term = args[0]['obesity_class' + i]
    refuted = args[0]['phenotype_refuted' + i]

    if hpo is None or term is None or refuted is None:
        return "Not recorded"

    label = []

    if refuted:
        label.append('Refuted ')
    label.append(term)
    label.append(f' ({hpo})')
    return ''.join(label)
