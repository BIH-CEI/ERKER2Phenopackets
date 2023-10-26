import uuid
from collections import deque
from typing import Dict, Optional, Union, Callable, Any

from .structure import compare_structure


def edit_distance(
        d1: Dict, d2: Dict,
        d1_id: Optional[Union[int, str]] = uuid.uuid4(),
        d2_id: Optional[Union[int, str]] = uuid.uuid4(),
        insertion_cost: Union[int, Callable[[Any], int]] = 1,
        val_substitution_cost: Union[int, Callable[[Any, Any], int]] = 1
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
    :param insertion_cost: Cost for inserting a key, can be a method taking the
    inserted element as a parameter, defaults to 1
    :type insertion_cost: Union[int, Callable[[Any], int]], optional
    :param val_substitution_cost: Cost for changing a value, can be a method taking
    the first and the second value as argument, defaults to 1
    :type val_substitution_cost: Union[int, Callable[[Any, Any], int]], optional
    :return: Edit distance between the two dictionaries
    :rtype: int
    """

    def check_cost_valid(cost_val: int, cost_label: str):
        """surround each cost call with this method to check if the cost is valid"""
        if not isinstance(cost_val, int) or cost_val < 0:
            raise ValueError(f'{cost_label} {cost_val} must be a non-negative '
                             f' integer')
        return cost_val

    if isinstance(insertion_cost, int):
        check_cost_valid(insertion_cost, 'insertion_cost')

        def insertion_cost(inserted):
            return insertion_cost

    if isinstance(val_substitution_cost, int):
        check_cost_valid(val_substitution_cost, 'val_substitution_cost')

        def val_substitution_cost(val1, val2):
            return val_substitution_cost

    equals, diff = compare_structure(
        d1, d2,
        d1_id, d2_id,
        include_vals=bool(val_substitution_cost),
        construct_diff_tree=False
    )

    if equals:
        return 0

    cost = 0

    q1 = deque()
    q1.append(d1)

    q2 = deque()
    q2.append(d2)

    while q1:
        n1, key_path1 = q1.popleft()
        n2, key_path2 = q2.popleft()

        if isinstance(n1, dict) and isinstance(n2, dict):
            for k1, v1, k2, v2 in zip(n1.keys(), n1.values(), n2.keys(), n2.values()):
                if k1 == k2:
                    q1.append(v1)
                    q2.append(v2)
                elif k1 != k2:
                    cost += _calculate_edit_distance(
                        subtree1={k1: v1},
                        subtree2={k2: v2},
                        insertion_cost=insertion_cost,
                        val_substitution_cost=val_substitution_cost
                    )

        elif (isinstance(n1, list) or isinstance(n1, tuple)) and \
                (isinstance(n2, list) or isinstance(n2, tuple)):
            if n1 != n2:
                cost += _calculate_edit_distance(
                    subtree1={'k': n1},
                    subtree2={'k': n2},
                    insertion_cost=insertion_cost,
                    val_substitution_cost=val_substitution_cost
                )

    return cost


def _calculate_edit_distance(subtree1: Dict, subtree2: Dict,
                             insertion_cost: int,
                             val_substitution_cost: int) -> int:
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
