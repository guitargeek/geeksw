import sys
import os
import pickle
import inspect
import time
import numpy as np
import re

from .helpers import *
from .DependencyGraph import DependencyGraph
from .Producers import Producer as GeekProducer
from .Producers import expand_wildcard

from ..data_formats import Particles

from types import FunctionType

import awkward
import h5py

import parsl
# from parsl.app.app import python_app, bash_app
from parsl.configs.local_threads import config

import glob


parsl.load(config)


awkward.persist.whitelist = awkward.persist.whitelist + [[u'awkward', u'Particles', u'frompairs']]


cache_dir = ".geeksw_cache"


class FuturesDummy(object):
    def done(self):
        return False


class MetaInfo(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def get_from_cache(product):

    filename = product.replace("/", "__")

    cache_file_name = os.path.join(cache_dir, filename + ".pkl")
    if os.path.isfile(cache_file_name):
        return pickle.load(open(cache_file_name, "rb"))

    cache_file_name = os.path.join(cache_dir, filename + ".h5")
    if os.path.isfile(cache_file_name):
        with h5py.File(cache_file_name) as hf:
            ah5 = awkward.hdf5(hf)
            return Particles.fromtable(ah5["product"])

    raise ValueError("Product "+product+" not found in cache!")


def load_module(name, path_to_file):
    if sys.version_info < (3, 0):
        import imp

        return imp.load_source(name, path_to_file)
    if sys.version_info < (3, 5):
        from importlib.machinery import SourceFileLoader

        return SourceFileLoader(name, path_to_file).load_module()
    else:
        import importlib.util

        spec = importlib.util.spec_from_file_location(name, path_to_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def load_producers(producers_path):
    producer_funcs = []
    hashes = []  # file hashes to track changes

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
            producer_funcs.append(func)
            hashes.append(func.func_hash)
    del file_name

    return producer_funcs


def get_exec_order(producers):
    graph = DependencyGraph(producers)
    return graph.toposort()


def cache(obj, name):

    name = name.replace("/", "__")

    # Saving JaggedArray stuff
    if type(obj) == Particles:
        file_name = os.path.join(path, name + ".h5")
        with h5py.File(file_name, "w") as hf:
            ah5 = awkward.hdf5(hf)
            ah5["product"] = obj.table()

        return os.path.getsize(file_name)

    # If there is no special rule, just try to pickle
    try:
        file_name = os.path.join(path, name + ".pkl")
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

    n = len(producer_funcs)
    matches = list(map(lambda P: ProductMatch(product, P), producer_funcs))
    # Penalize matching depth score with number of template specializations
    # to give priority to full specializations.
    scores = [m.score - len(m.subs) / 100.0 for m in matches]
    if max(scores) == 0:
        return []
    i = np.argmax(scores)

    working_dir = product[: -len(matches[i].group)]
    producers = [GeekProducer(producer_funcs[i], matches[i].subs, working_dir, datasets)]

    for i, req in enumerate(producers[0].expand_full_requires(flatten=True)):
        producers += get_required_producers(req, producer_funcs, datasets, record)

    return producers


def produce(products=None,
            producers=[],
            datasets=None,
            cache_time=2,
    ):

    target_products = products

    # Create the cache dir structure
    mkdir(cache_dir)

    if type(producers) == str:
        producer_funcs = load_producers(producers)
    else:
        producer_funcs = producers

    producers = []

    target_products = [expand_wildcard(t[1:], datasets) for t in target_products]
    target_products = [y for x in target_products for y in x]

    record = {}

    for t in target_products:
        producers += get_required_producers(t, producer_funcs, datasets, record)
    producers = list(set(producers))

    exec_order = get_exec_order(producers)

    print("Producers:")
    for i, ip in enumerate(exec_order):
        print(
            " ".join(
                ["{0}.".format(i)]
                + producers[ip].requires
                + ["->", producers[ip].product]
            )
        )

    def run_producer(producer):

        pname = producer.full_product
        print("Producing " + pname + "...")

        working_dir = producer.working_dir
        inputs = {}
        for req, full_req in zip(producer.input_names, producer.full_requires_expanded):
            if len(full_req) > 1:
                inputs[req] = [(x, record[x]) for x in full_req]
            else:
                inputs[req] = record[full_req[0]]

        if producer.run.is_template:
            inputs["meta"] = MetaInfo(subs = producer.subs,
                                      working_dir = producer.working_dir)

        return producer.run(**inputs)

    launched = [[False] for i in range(len(producers))]
    futures = [FuturesDummy() for i in range(len(producers))]
    start_times = [None] * len(producers)
    elapsed_times = [None] * len(producers)

    # Loop over producers needed to get to the desired output products
    while exec_order:

        for i, ip in enumerate(exec_order):

            requirements = producers[ip].expand_full_requires(flatten=True)

            requirements_available = True
            for x in requirements:
                if x not in record.keys():
                    requirements_available = False
                    break

            if not requirements_available:
                continue

            if not launched[ip][0]:
                futures[ip] = run_producer(producers[ip])
                launched[ip][0] = True
                start_times[ip] = time.time()

            if not futures[ip].done():
                continue

            elapsed_times[ip] = time.time() - start_times[ip]
            start_times[ip] = None

            record[producers[ip].full_product] = futures[ip].result()

            if elapsed_times[ip] > cache_time:
                print("Pruducer time longer than 2 seconds, caching product...")
                pname = producers[ip].full_product
                size = cache(record[pname], pname)
                if size > 0:
                   print("Cached product {0}: {1}".format(pname, humanbytes(size)))

            exec_order.pop(i)

            requirements_all = []
            for i, producer in enumerate(producers):
                if i in exec_order:
                    requirements_all += producer.expand_full_requires(flatten=True)

            for key in list(record.keys()):
                if key not in requirements_all and key not in target_products:
                    del record[key]

    return record
