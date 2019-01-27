import sys
import os
import pickle
import inspect
import threading
import time

from .helpers import *
from .DependencyGraph import DependencyGraph
from .Plot import Plot
from .Producers import Producer as GeekProducer
from .Producers import expand_wildcard


class MetaInfo(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class Dataset(object):
    def __init__(self, file_path, geeksw_path):
        self.file_path = file_path
        self.geeksw_path = geeksw_path


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


def get_producer_funcs(producers_path):
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
            hashes += hash_file(file_path)
    del file_name

    return producer_funcs


def get_exec_order(producers):
    graph = DependencyGraph(producers)
    return graph.toposort()


def save(obj, name, path):

    # How to save matplotlib plots
    if type(obj) == Plot:
        return obj.save(path, name)

    # If there is no special rule, just pickle
    file_name = os.path.join(path, name + ".pkl")
    mkdir(os.path.dirname(file_name))
    with open(file_name, "wb") as f:
        pickle.dump(obj, f)
    return os.path.getsize(file_name)


import re


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


import numpy as np


def get_required_producers(product, producer_funcs, out_dir):

    n = len(producer_funcs)
    matches = list(map(lambda P: ProductMatch(product, P), producer_funcs))
    # Penalize matching depth score with number of template specializations
    # to give priority to full specializations.
    scores = [m.score - len(m.subs) / 100.0 for m in matches]
    if max(scores) == 0:
        return []
    i = np.argmax(scores)

    working_dir = product[: -len(matches[i].group)]
    producers = [GeekProducer(producer_funcs[i], matches[i].subs, working_dir, out_dir)]

    for i, req in enumerate(producers[0].expand_full_requires(flatten=True)):
        producers += get_required_producers(req, producer_funcs, out_dir)

    return producers


def geek_run(config):

    try:
        # Try to open the file to see if it's a valid file path
        with open(config, "r") as f:
            pass
    except:
        # If the passed config was not a file, maybe if was a string that is
        # supposed to be the content of the config...
        import tempfile
        import subprocess

        new_file, filename = tempfile.mkstemp()

        os.write(new_file, str.encode(config))
        os.close(new_file)

        subprocess.call(["mv", filename, filename + ".py"])

        config = filename + ".py"

    config = load_module("config", config)

    producers_path = config.producers
    target_products = config.products

    cache_dir = config.cache_dir if hasattr(config, "cache_dir") else "cache"
    out_dir = config.out_dir if hasattr(config, "out_dir") else "output"

    # Create list of dataset instances from configuration tuples
    datasets = [Dataset(*args) for args in config.datasets]

    # Create the output dir structure
    os.system("rm -rf " + out_dir)  # Delete previous output to not confuse glob
    for ds in datasets:
        mkdir(os.path.join(out_dir, "." + ds.geeksw_path))

    producer_funcs = get_producer_funcs(producers_path)
    producers = []

    target_products = [expand_wildcard(t[1:], out_dir) for t in target_products]
    target_products = [y for x in target_products for y in x]

    for t in target_products:
        producers += get_required_producers(t, producer_funcs, out_dir)
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

    record = {}

    def run_producer(producer):

        pname = producer.full_product
        print("Producing " + pname + "...")

        working_dir = producer.working_dir
        inputs = {}
        for req, full_req in zip(
            producer.input_names, producer.full_requires_expanded
        ):
            if len(full_req) > 1:
                inputs[req] = [(x, record[x]) for x in full_req]
            else:
                inputs[req] = record[full_req[0]]

        if producer.run._is_template:
            inputs["meta"] = MetaInfo(subs = producer.subs,
                                      working_dir = producer.working_dir)

        class ProducerThread(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)

            def run(self):
                product = producer.run(**inputs)

                # time.sleep(2)

                record[pname] = product

                if producer.cache:
                    size = save(product, pname, cache_dir)
                    print("Caching product {0}: {1}".format(pname, humanbytes(size)))

                if pname in target_products:
                    size = save(product, pname, out_dir)
                    print("Saving output {0}: {1}".format(pname, humanbytes(size)))



        t = ProducerThread()
        t.start()


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

            run_producer(producers[ip])

            exec_order.pop(i)

            requirements_all = []
            for i, producer in enumerate(producers):
                if i in exec_order:
                    requirements_all += producer.expand_full_requires(flatten=True)

            for key in list(record.keys()):
                if key not in requirements_all:
                    del record[key]

    return record
