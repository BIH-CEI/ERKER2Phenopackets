from ERKER2Phenopackets.src.analysis.comparison.structure import assign_dict_at, \
    create_difference_tree, compare_structure


def test_assign_dict_at():
    d1 = {'a': {'b': {}}}
    assert (assign_dict_at(
        d=d1,
        key_path=['a', 'b', 'c'],
        value=[2]
    ) == {'a': {'b': {'c': [2]}}})

    assert (assign_dict_at(
        d=d1,
        key_path=['a', 'b', 'c', 0],
        value=3
    ) == {'a': {'b': {'c': [3]}}})


def test_create_difference_tree():
    d1 = {'a': {'b': {'c': 2}}}
    d2 = {'a': {'b': {'c': 3}}}
    diff = create_difference_tree(d1, d2, 1, 2)
    expected = {'a': {'b': {'c': {1: 2, 2: 3}}}}
    assert diff == expected

    d3 = {'a': {'b': {'d': 2}}}
    diff = create_difference_tree(d1, d3, 1, 3)
    expected = {'a': {'b': {1: {'c': 2}, 3: {'d': 2}}}}
    assert diff == expected

    d4 = {'a': {'b': {'c': [2]}}}
    d5 = {'a': {'b': {'c': [3]}}}
    diff = create_difference_tree(d4, d5, 4, 5)
    expected = {'a': {'b': {'c': {4: [2], 5: [3]}}}}
    assert diff == expected


def test_compare_structure():
    d1 = {'a': {'b': {'c': 2}}}
    d2 = {'a': {'b': {'c': 3}}}
    equals, diff = compare_structure(d1, d2, 1, 2)
    expected = {}
    assert equals
    assert diff == expected

    d3 = {'a': {'b': {'d': 2}}}
    equals, diff = compare_structure(d1, d3, 1, 3)
    expected = {'a': {'b': {1: {'c': 2}, 3: {'d': 2}}}}
    assert not equals
    assert diff == expected

    d4 = {'a': {'b': {'c': [2]}}}
    d5 = {'a': {'b': {'c': [3]}}}
    equals, diff = compare_structure(d4, d5, 4, 5)
    expected = {'a': {'b': {'c': {4: [2], 5: [3]}}}}
    assert equals
    assert diff == expected
