from collections import deque
from typing import Dict, List


def traverse(d: Dict, order: str = 'bfs', include_vals: bool = True) -> List:
    """Traverse a dictionary in a specific order.

    :param d: Dictionary to traverse
    :type d: Dict
    :param order: Order to traverse the dictionary in either 'bfs' or 'dfs', defaults to
    'bfs'
    :type order: str, optional
    :param include_vals: Whether to include values in the traversal, defaults to True
    :type include_vals: bool, optional
    :return: List of keys and values in the order they were traversed
    :rtype: List
    """
    if order == 'bfs':
        return bfs(d, include_vals)
    elif order == 'dfs':
        return dfs(d, include_vals)
    else:
        raise ValueError(f'Order {order} not supported')


def bfs(d: Dict, include_vals: bool = True) -> List:
    traversal = []

    queue = deque()
    queue.append(d)

    while queue:
        node = queue.popleft()

        if isinstance(node, dict):
            for key, value in zip(node.keys(), node.values()):
                traversal.append(key)
                queue.append(value)
        elif isinstance(node, list) or isinstance(node, tuple):
            traversal.append('list')
            for value in node:
                queue.append(value)
        elif include_vals:
            traversal.append(node)

    return traversal


def dfs(d: Dict, include_vals: bool = True) -> List:
    traversal = []

    stack = [d]

    while stack:
        node = stack.pop()

        if isinstance(node, dict):
            for key, value in zip(reversed(list(node.keys())),
                                  reversed(list(node.values()))):
                stack.append(value)
                traversal.append(key)
        elif isinstance(node, list) or isinstance(node, tuple):
            traversal.append('list')
            for value in reversed(node):
                stack.append(value)
        elif include_vals:
            traversal.append(node)

    return traversal


if __name__ == '__main__':
    tree = {
        'A': {
            'B': {
                'D': {},
                'E': {},
            },
            'C': {
                'F': {},
                'G': {},
            },
        }
    }

    print(tree)

    print(traverse(tree))
    print(traverse(tree, 'dfs'))
