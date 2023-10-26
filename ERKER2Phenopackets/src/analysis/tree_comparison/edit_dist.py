import uuid
from collections import deque
from typing import Dict, Optional, Union

from .structure import compare_structure


def edit_distance(
        d1: Dict, d2: Dict,
        d1_id: Optional[Union[int, str]] = uuid.uuid4(),
        d2_id: Optional[Union[int, str]] = uuid.uuid4(),
        insertion_cost: int = 1,
        val_change_cost: int = 1,
) -> int:
    """
    Calculates the edit distance between two dictionaries.


    TODO: in the future also support functions that have access to the values for
    cost calculation

    :param d1: First dictionary
    :type d1: Dict
    :param d2: Second dictionary
    :type d2: Dict
    :param d1_id: Identifier for first dictionary, defaults to random UUID
    :type d1_id: Optional[Union[int, str]], optional
    :param d2_id: Identifier for second dictionary, defaults to random UUID
    :type d2_id: Optional[Union[int, str]], optional
    :param insertion_cost: Cost for inserting a key, defaults to 1
    :type insertion_cost: int, optional
    :param val_change_cost: Cost for changing a value, defaults to 1
    :type val_change_cost: int, optional
    :return: Edit distance between the two dictionaries
    :rtype: int
    """
    def check_cost_valid(cost_val: int, cost_label:str):
        """surround each cost call with this method to check if the cost is valid"""
        if not isinstance(cost_val, int) or cost_val < 0:
            raise ValueError(f'{cost_label} {cost_val} must be a non-negative '
                             f' integer')
        return cost_val

    check_cost_valid(insertion_cost, 'insertion_cost')
    check_cost_valid(val_change_cost, 'val_change_cost')

    equals, diff = compare_structure(
        d1, d2,
        d1_id, d2_id,
        include_vals=bool(val_change_cost)
    )

    if equals:
        return 0

    # traverse through the difference tree and calculate the edit distance
    cost = 0
    queue = deque()
    queue.append(diff)

    while queue:
        node = queue.popleft()

        if isinstance(node, dict):
            if len(node.keys()) == 2 and d1_id in node and d2_id in node:
                cost += _calculate_edit_distance(
                    subtree1=node[d1_id],
                    subtree2=node[d2_id],
                    insertion_cost=insertion_cost,
                    val_change_cost=val_change_cost
                )
            else:
                for key, value in zip(node.keys(), node.values()):
                    queue.append(value)

        elif isinstance(node, list) or isinstance(node, tuple):
            for value in node:
                queue.append(value)
        # no need to handle leaf nodes, if they are different, they will be surrounded
        # by a dict with the two identifiers as keys

    return cost


def _calculate_edit_distance(subtree1: Dict, subtree2: Dict,
                             insertion_cost: int,
                             val_change_cost: int) -> int:
    """
    Calculates the edit distance between two subtrees.

    :param subtree1: First subtree
    :type subtree1: Dict
    :param subtree2: Second subtree
    :type subtree2: Dict
    :param insertion_cost: Cost for inserting a key, defaults to 1
    :type insertion_cost: int, optional
    :param val_substitution_cost: Cost for changing a value, defaults to 1
    :type val_substitution_cost: int, optional
    :return: Edit distance between the two subtrees
    :rtype: int
    """
    pass
