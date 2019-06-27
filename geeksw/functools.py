from functools import *

def anymap(func, l, x):
    """ check if func(x, y) for any y in l is true
    """
    return any(map(partial(func, x), l))


def allmap(func, l, x):
    """ check if func(x, y) for all y in l is true
    """
    return all(map(partial(func, x), l))


def filteranymap(func, l1, l2):
    """ Select all x from a for which func(x, y) for any y in l is true
    """
    return filter(partial(anymap, func, l1), l2)


def filterallmap(func, l1, l2):
    """ Select all x from a for which func(x, y) for all y in l is true
    """
    return filter(partial(allmap, func, l1), l2)


def contains(x, y):
    return y in x


def startswith(x, y):
    return x.startswith(y)


def endswith(x, y):
    return x.endswith(y)
