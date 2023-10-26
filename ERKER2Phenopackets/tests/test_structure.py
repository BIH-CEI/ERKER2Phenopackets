from ERKER2Phenopackets.src.analysis.comparison.structure import assign_dict_at


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
