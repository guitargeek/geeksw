import os
import pickle
import inspect
import time
import numpy as np
import re
import awkward
import h5py
import glob

from .utils import *
from .dependencies import *
from .Producers import ProducerWrapper
from .Producers import expand_wildcard


cache_dir = ".geeksw_cache"


def get_from_cache(product):

    filename = product.replace("/", "__")

    cache_file_name = os.path.join(cache_dir, filename + ".pkl")
    if os.path.isfile(cache_file_name):
        return pickle.load(open(cache_file_name, "rb"))

    raise ValueError("Product "+product+" not found in cache!")


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


def cache(obj, name):

    name = name.replace("/", "__")

    try:
        file_name = os.path.join(cache_dir, name + ".pkl")
        with open(file_name, "wb") as f:
            pickle.dump(obj, f)
        return os.path.getsize(file_name)
    except pickle.PicklingError as e:
        print("Product "+name+" could not be pickled.")
        return -1


class ProductMatch(object):
    def __init__(self, product, producer):

        regex = re.sub("<[^<>]*>", "[^/]*", producer.product)
        match = re.match(".*" + regex + "$", product)

        if match is None:
            self.group = None
            self.subs = {}
            self.score = 0
            return

        depth = producer.product.count("/")

        # The matching pattern
        self.group = "/".join(match.group().split("/")[-depth - 1 :])
        # The "matching depth". Products which match deeper are resolving ambiguities.
        self.score = self.group.count("/") + 1

        # hotfix for problem in pattern matching:
        # producers where the last identifier in the path is matched are usually to be favoured
        if producer.product.split("/")[-1] == product.split("/")[-1]:
            self.score = self.score + 100

        # The substitutions for the template specialization
        self.subs = {}
        for t, s in zip(producer.product.split("/"), self.group.split("/")):
            if t != s:
                self.subs[t] = s


def get_required_producers(product, producer_funcs, datasets, record):

    cache_file_wo_suffix = os.path.join(cache_dir, product.replace("/", "__"))
    if glob.glob(cache_file_wo_suffix + "*"):
        record[product] = get_from_cache(product)
        return []

    matches = [ProductMatch(product, f) for f in producer_funcs]
    # Penalize matching depth score with number of template specializations
    # to give priority to full specializations.
    scores = [m.score - len(m.subs) / 100.0 for m in matches]
    if max(scores) == 0:
        return []
    i = np.argmax(scores)

    working_dir = product[: -len(matches[i].group)]
    producers = [ProducerWrapper(producer_funcs[i], matches[i].subs, working_dir, datasets)]

    for req in producers[0].flattened_requirements:
        producers += get_required_producers(req, producer_funcs, datasets, record)

    return producers


def produce(products=None,
            producers=[],
            datasets=None,
            max_workers=32,
            cache_time=2,
    ):

    target_products = products

    # Create the cache dir structure
    mkdir(cache_dir)

    if isinstance(producers, str):
        producers = load_producers(producers)

    producer_instances = []

    target_products = [expand_wildcard(t[1:], datasets) for t in target_products]
    target_products = [y for x in target_products for y in x]

    record = {}

    for t in target_products:
        producer_instances += get_required_producers(t, producers, datasets, record)

    producers = list(set(producer_instances))

    exec_order = toposort(make_dependency_graph(producers))

    print("Producers:")
    for i, ip in enumerate(exec_order):
        print("{0}. ".format(i) + producers[ip].description)


    # Loop over producers needed to get to the desired output products
    for i, ip in enumerate(exec_order):

        start_time = time.time()

        pname = producers[ip].product
        print("Producing " + pname + "...")

        record[producers[ip].product] = producers[ip].run(record)

        requirements_all = []
        for i, producer in enumerate(producers):
            if i in exec_order:
                requirements_all += producer.flattened_requirements

        if time.time() - start_time > cache_time:
            print("Pruducer time longer than 2 seconds, caching product...")
            pname = producers[ip].product
            size = cache(record[pname], pname)
            if size > 0:
               print("Cached product {0}: {1}".format(pname, humanbytes(size)))

        for key in list(record.keys()):
            if key not in requirements_all and key not in target_products:
                del record[key]

    return record
