"""General-purpose utilities to work with parsed data structures."""


def remove_empty_dicts(iter_of_dicts):
    """Remove empty dictionaries from an iterable of dicts.

    :param iter_of_dicts: iterable of dicts
    :return: iterable with empty dicts removed
    """
    return filter(lambda x: len(x) > 0, iter_of_dicts)


def transpose_list(list_of_dicts):
    """Transpose a list of dicts to a dict of lists.

    :param list_of_dicts: to transpose, as in the output from a parse call
    :return: Dict of lists
    """
    res = {}
    for d in list_of_dicts:
        for k, v in d.items():
            if k in res:
                res[k].append(v)
            else:
                res[k] = [v]
    return res
