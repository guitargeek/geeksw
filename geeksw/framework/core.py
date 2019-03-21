import os
import time
import numpy as np
import re
import awkward
import h5py
from .utils import *
from .dependencies import *
from .ProducerWrapper import ProducerWrapper, expand_wildcard
from .cache import FrameworkCache


def load_producers(producers_path):
    producers = []

    for file_name in os.listdir(producers_path):
        if file_name == "__init__.py" or file_name[-3:] != ".py":
            continue
        name = file_name[:-3]
        module = load_module(name, os.path.join(producers_path, file_name))
        for item in dir(module):
            func = getattr(module, item)
            if not hasattr(func, "product") or not hasattr(func, "requirements"):
                continue
            file_path = os.path.join(producers_path, file_name)
            producers.append(func)
    del file_name

    return producers


def match_product(product, func, verbose=False):

    if verbose:
        print("Matching product "+product+"...")

    regex = re.sub("<[^<>]*>", "[^/]*", func.product)
    match = re.match(".*" + regex + "$", product)

    if match is None:
        return None, 0

    depth = func.product.count("/")

    # The matching pattern
    group = "/".join(match.group().split("/")[-depth - 1 :])
    # The "matching depth". Products which match deeper are resolving ambiguities.
    score = group.count("/") + 1

    # hotfix for problem in pattern matching:
    # producer functions where the last identifier in the path is matched are usually to be favoured
    if func.product.split("/")[-1] == product.split("/")[-1]:
        score = score + 100

    # Penalize matching depth score with number of template specializations
    # to give priority to full specializations.
    score = score - len(group.split("/")) / 100.0

    if verbose:
        print(func.product, score)

    return group, score


def get_required_producers(product, producer_funcs, datasets, record, cache):

    if product in cache:
        record[product] = cache[product]
        return []

    groups, scores = zip(*[match_product(product, f) for f in producer_funcs])

    if max(scores) == 0:
        return []
    i = np.argmax(scores)

    func, group = producer_funcs[i], groups[i]

    # The substitutions for the template specialization
    subs = {t: s for t, s in zip(func.product.split("/"), group.split("/")) if t != s}

    working_dir = product[: -len(group)]
    producers = [ProducerWrapper(func, subs, working_dir, datasets)]

    for req in producers[0].flattened_requirements:
        producers += get_required_producers(req, producer_funcs, datasets, record, cache)

    return producers


def produce(
    products=None, producers=[], datasets=None, max_workers=32, cache_time=2, verbosity=1, cache_dir=".geeksw_cache"
):

    target_products = products

    cache = FrameworkCache(cache_dir=cache_dir)

    if isinstance(producers, str):
        producers = load_producers(producers)

    producer_instances = []

    target_products = [expand_wildcard(t[1:], datasets) for t in target_products]
    target_products = [y for x in target_products for y in x]

    record = {}

    for t in target_products:
        producer_instances += get_required_producers(t, producers, datasets, record, cache)

    producers = list(set(producer_instances))

    exec_order = toposort(make_dependency_graph(producers))

    if verbosity > 0:
        print("Producers:")
        for i, ip in enumerate(exec_order):
            print("{0}. ".format(i) + producers[ip].description)

    # Loop over producers needed to get to the desired output products
    for i, ip in enumerate(exec_order):

        start_time = time.time()

        pname = producers[ip].product
        if verbosity > 0:
            print("Producing " + pname + "...")

        record[producers[ip].product] = producers[ip].run(record)

        requirements_all = []
        for ipremain in exec_order[i + 1 :]:
            requirements_all += producers[ipremain].flattened_requirements

        if producers[ip].cache and time.time() - start_time > cache_time:
            print("Pruducer time longer than {0:.2f} seconds, caching product...".format(cache_time))
            pname = producers[ip].product
            cache[pname] = record[pname]

        for key in list(record.keys()):
            if key not in requirements_all and key not in target_products:
                del record[key]

    return record
