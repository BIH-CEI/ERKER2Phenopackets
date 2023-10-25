import uuid
from typing import Dict, Tuple, Union, Optional

from .traverse import traverse


def compare_structure(
        d1: Dict, d2: Dict,
        d1_id: Optional[Union[int, str]] = uuid.uuid4(),
        d2_id: Optional[Union[int, str]] = uuid.uuid4()
) -> Tuple[bool, Dict]:
    """Compares if the structure of two dictionaries match.

    By structure we mean the keys and the order of the keys.

    TODO: WARNING currently does not return a difference tree, but only a boolean

    :param d1: First dictionary
    :type d1: Dict
    :param d2: Second dictionary
    :type d2: Dict
    :param d1_id: Identifier for first dictionary, defaults to random UUID
    :type d1_id: Optional[Union[int, str]], optional
    :param d2_id: Identifier for second dictionary, defaults to random UUID
    :type d2_id: Optional[Union[int, str]], optional
    :return: True if structure matches, False and difference dict otherwise
    """
    bfs1 = traverse(d1, 'bfs', include_vals=False)
    bfs2 = traverse(d2, 'bfs', include_vals=False)

    if not bfs1 == bfs2:
        return False, create_difference_tree(d1, d2, d1_id, d2_id)

    dfs1 = traverse(d1, 'dfs', include_vals=False)
    dfs2 = traverse(d2, 'dfs', include_vals=False)

    if not dfs1 == dfs2:
        return False, create_difference_tree(d1, d2, d1_id, d2_id)

    return True, {}
