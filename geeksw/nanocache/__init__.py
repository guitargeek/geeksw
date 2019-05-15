from .Dataset import *
from .ScratchCache import *
from .UprootIOWrapper import *


def trim_name(name):
    # make sure there are no duplicate dashes
    l = len(name)
    l_new = -1
    while l_new != l:
        l = len(name)
        name = name.replace("//", "/")
        l_new = len(name)

    # make sure dataset name starts with a dash
    if not name.startswith("/"):
        name = "/" + name

    return name


def load_datasets(names, cache=ScratchCache(), server="root://polgrid4.in2p3.fr"):

    if type(names) == str:
        names = [names]
    if type(names) == list:
        names = [trim_name(n) for n in sorted(names)]
        datasets = [Dataset(n, server) for n in names]
    else:
        raise TypeError("Argument names has to be string or list")

    return UprootIOWrapper(datasets=datasets, cache=cache)


def load_dataset(name, cache=ScratchCache(), server="root://polgrid4.in2p3.fr"):
    return load_datasets([name], cache=cache, server=server)
