import uuid
from collections import deque
from typing import Dict, Optional, Union, Callable, Any

from .structure import compare_structure

T = Union[int, float]


def edit_distance(
        d1: Dict, d2: Dict,
        d1_id: Optional[Union[int, str]] = uuid.uuid4(),
        d2_id: Optional[Union[int, str]] = uuid.uuid4(),
        subtree_substitution_cost: T = 1,
        insertion_cost: Union[int, float, Callable[[Any], T]] = 1,
        val_substitution_cost: Union[int, float, Callable[[Any, Any], T]] = 1
) -> T:
    """
    Calculates the edit distance between two dictionaries.

    :param d1: First dictionary
    :type d1: Dict
    :param d2: Second dictionary
    :type d2: Dict
    :param d1_id: Identifier for first dictionary, defaults to random UUID
    :type d1_id: Optional[Union[int, str]], optional
    :param d2_id: Identifier for second dictionary, defaults to random UUID
    :type d2_id: Optional[Union[int, str]], optional
    :param subtree_substitution_cost: Cost for changing a subtree, if this is assigned,
    insertion cost and substitution cost are ignored, defaults 1
    :type subtree_substitution_cost: Union[int, float]
    :param insertion_cost: Cost for inserting a key, can be a method taking the
    inserted element as a parameter, defaults to 1
    :type insertion_cost: Union[int, float, Callable[[Any], Union[int, float]]]
    :param val_substitution_cost: Cost for changing a value, can be a method taking
    the first and the second value as argument, defaults to 1
    :type val_substitution_cost:
    Union[int, float, Callable[[Any, Any], Union[int, float]]]
    :return: Edit distance between the two dictionaries
    :rtype: int
    """

    def check_cost_valid(cost_val: T, cost_label: str):
        """surround each cost call with this method to check if the cost is valid"""
        if not isinstance(cost_val, (int, float)) or cost_val < 0:
            raise ValueError(f'{cost_label} {cost_val} must be a non-negative '
                             f' integer or floating point number')
        return cost_val

    if isinstance(subtree_substitution_cost, (int, float)):
        check_cost_valid(
            subtree_substitution_cost,
            'subtree_substitution_cost'
        )

    if isinstance(insertion_cost, (int, float)):
        check_cost_valid(insertion_cost, 'insertion_cost')

        def insertion_cost(inserted):
            return insertion_cost

    if isinstance(val_substitution_cost, (int, float)):
        check_cost_valid(val_substitution_cost, 'substitution_cost')

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


def _calculate_edit_distance(
        subtree1: Dict, subtree2: Dict,
        insertion_cost: Union[int, float, Callable[[Any], T]] = 1,
        val_substitution_cost: Union[int, float, Callable[[Any, Any], T]] = 1
) -> T:
    """
    Calculates the edit distance between two subtrees.

    :param subtree1: First subtree
    :type subtree1: Dict
    :param subtree2: Second subtree
    :type subtree2: Dict
    :param subtree_change_cost: Cost for changing a subtree, if this is assigned,
    insertion cost and substitution cost are ignored, defaults 1
    :type subtree_substitution_cost: Union[int, float]
    :param insertion_cost: Cost for inserting a key, can be a method taking the
    inserted element as a parameter, defaults to 1
    :type insertion_cost: Union[int, float, Callable[[Any], Union[int, float]]]
    :param val_substitution_cost: Cost for changing a value, can be a method taking
    the first and the second value as argument, defaults to 1
    :type val_substitution_cost:
    Union[int, float, Callable[[Any, Any], Union[int, float]]]
    :return: Edit distance between the two subtrees
    :rtype: int
    """
    if subtree_substitution_cost:
        return subtree_substitution_cost
    # TODO: the structure of the subtrees should roughly match, assign penalties
    #  otherwise
    return 1
