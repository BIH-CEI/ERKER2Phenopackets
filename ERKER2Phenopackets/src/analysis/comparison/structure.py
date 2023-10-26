import uuid
from collections import deque
from typing import Dict, Tuple, Union, Optional, List, Any

from .traverse import traverse


def compare_structure(
        d1: Dict, d2: Dict,
        d1_id: Optional[Union[int, str]] = uuid.uuid4(),
        d2_id: Optional[Union[int, str]] = uuid.uuid4(),
        include_vals: bool = False
) -> Tuple[bool, Dict]:
    """Compares if the structure of two dictionaries match.

    By structure we mean the keys and the order of the keys.

    :param d1: First dictionary
    :type d1: Dict
    :param d2: Second dictionary
    :type d2: Dict
    :param d1_id: Identifier for first dictionary, defaults to random UUID
    :type d1_id: Optional[Union[int, str]], optional
    :param d2_id: Identifier for second dictionary, defaults to random UUID
    :type d2_id: Optional[Union[int, str]], optional
    :param include_vals: Whether to include values in the comparison, defaults to False
    because this method is mainly concerned with the structure of the tree
    :type include_vals: bool, optional
    :return: True if structure matches, False and difference dict otherwise
    """
    bfs1 = traverse(d1, 'bfs', include_vals=include_vals)
    bfs2 = traverse(d2, 'bfs', include_vals=include_vals)

    if not bfs1 == bfs2:
        return False, create_difference_tree(d1, d2, d1_id, d2_id)

    dfs1 = traverse(d1, 'dfs', include_vals=include_vals)
    dfs2 = traverse(d2, 'dfs', include_vals=include_vals)

    if not dfs1 == dfs2:
        return False, create_difference_tree(d1, d2, d1_id, d2_id)

    return True, {}


def create_difference_tree(d1: Dict, d2: Dict,
                           d1_id: Optional[Union[int, str]] = uuid.uuid4(),
                           d2_id: Optional[Union[int, str]] = uuid.uuid4()
                           ) -> Dict:
    """Creates a difference tree for two dictionaries.

    :param d1: First dictionary
    :type d1: Dict
    :param d2: Second dictionary
    :type d2: Dict
    :param d1_id: Identifier for first dictionary, defaults to random UUID
    :type d1_id: Optional[Union[int, str]], optional
    :param d2_id: Identifier for second dictionary, defaults to random UUID
    :type d2_id: Optional[Union[int, str]], optional
    :return: Difference tree
    :rtype: Dict
    """
    difference_tree = {}
    q1 = deque()
    q1.append((d1, [None]))

    q2 = deque()
    q2.append((d2, [None]))

    while q1:
        n1, key_path1 = q1.popleft()
        n2, key_path2 = q2.popleft()

        if isinstance(n1, dict) and isinstance(n2, dict):
            for k1, v1, k2, v2 in zip(n1.keys(), n1.values(), n2.keys(), n2.values()):
                if k1 == k2:
                    difference_tree = assign_dict_at(
                        d=difference_tree,
                        key_path=key_path1,
                        value={k1: {}}
                    )

                    q1.append((v1, key_path1 + [k1]))
                    q2.append((v2, key_path2 + [k2]))
                elif k1 != k2:
                    difference_tree = assign_dict_at(
                        d=difference_tree,
                        key_path=key_path1,
                        value={
                            d1_id: {k1: v1},
                            d2_id: {k2: v2},
                        }
                    )

        elif (isinstance(n1, list) or isinstance(n1, tuple)) and \
                (isinstance(n2, list) or isinstance(n2, tuple)):
            if n1 == n2:
                difference_tree = assign_dict_at(
                    d=difference_tree,
                    key_path=key_path1,
                    value=n1
                )
            elif n1 != n2:
                difference_tree = assign_dict_at(
                    d=difference_tree,
                    key_path=key_path1,
                    value={
                        d1_id: n1,
                        d2_id: n2,
                    }
                )
        else:
            difference_tree = assign_dict_at(
                d=difference_tree,
                key_path=key_path1,
                value={
                    d1_id: n1,
                    d2_id: n2,
                }
            )

    return difference_tree


def assign_dict_at(d: Dict, key_path: List[Union[str, int]], value: Any) -> Dict:
    """
    Assigns a value to a dictionary at a given key path.

    Example:

    >>> d = {'a': {'b': {}}}
    >>> assign_dict_at(d, ['a', 'b', 'c'], 2)
    {'a': {'b': {'c': 2}}}

    :param d: a dictionary
    :type d: Dict
    :param key_path: a list of keys to traverse the dictionary with to get to the value
    :type key_path: List[Union[str, int]]
    :param value: the value to assign at the position specified by the key path
    :type value: Any
    :return: the dictionary with the value assigned at the position specified by the key
     path
    :rtype: Dict
    """
    _d = d
    for key in key_path[:-1]:
        if key is None:
            continue
        if key in _d:
            _d = _d[key]
        else:
            _d[key] = {}
            _d = _d[key]

    if key_path[-1] is not None:
        _d[key_path[-1]] = value
    elif isinstance(value, dict):
        return value
    elif isinstance(value, (int, str)):
        return {value: {}}
    else:
        raise ValueError(f'Could not insert {value} at {key_path} in {d}')

    return d
