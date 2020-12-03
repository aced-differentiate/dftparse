from dftparse.util import remove_empty_dicts
from dftparse.util import transpose_list


def test_remove_empty_dicts():
    """Test that remove empty dictionaries works."""
    lst = [{}, {"foo": "bar"}, {}, {}, {"spam": "eggs"}, {}]
    clean = list(remove_empty_dicts(lst))
    assert(len(clean) == 2)
    assert(clean[0] == {"foo": "bar"})
    assert(clean[1] == {"spam": "eggs"})


def test_transpose_list():
    """Test that transpose list works."""
    lst = [{"b": 1.0}, {"a": 1.0, "b": 2.0}, {"a": 2.0, "b": 4.0}, {"a": 4.0}]
    foo = transpose_list(lst)
    assert(len(foo) == 2)
    assert("a" in foo)
    assert("b" in foo)
    assert(foo["a"] == [1.0, 2.0, 4.0])
    assert(foo["b"] == [1.0, 2.0, 4.0])
