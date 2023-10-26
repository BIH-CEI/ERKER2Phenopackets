from ERKER2Phenopackets.src.analysis.tree_comparison.edit_dist import edit_distance


def test_same():
    d1 = {'a': {'b': {'c': 2}}}
    assert edit_distance(d1, d1) == 0

    d2 = {'a': {'b': {'c': [2, 3, 4, 5]}}}
    assert edit_distance(d2, d2) == 0


def test_insertion():
    pass


def test_substitution():
    pass


def test_subtree_substitution():
    d1 = {'a': {'b': {'c': 2}, 'd': {'e': 3}}}
    d2 = {'a': {'b': {'c': 2}, 'g': {'h': 4}}}

    assert edit_distance(d1, d2) == 1

