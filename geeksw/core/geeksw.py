import sys
import os
import pickle
import inspect
import glob

from .helpers import *
from .DependencyGraph import DependencyGraph
from .Plot import Plot
from .Record import Record, FullRecord, Dataset
from .Producers import Producer as GeekProducer

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def path_product(p1, p2):
    return [os.path.join(*x) for x in itertools.product(p1, p2)]

def expand_wildcard(product, out_dir):
    i = product[::-1].find("*")
    wildcard_expr = os.path.join(out_dir, product[:-i])
    rest = product[-i:]
    return [path[len(out_dir):] + rest for path in glob.glob(wildcard_expr)]

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


def get_producer_classes(producers_path):
    Producers = []
    hashes = [] # file hashes to track changes

    for file_name in os.listdir(producers_path):
        if file_name == '__init__.py' or file_name[-3:] != '.py':
            continue
        name = file_name[:-3]
        module = load_module(name, os.path.join(producers_path,file_name))
        for item in dir(module):
            Producer = getattr(module, item)
            if not inspect.isclass(Producer) or not GeekProducer in Producer.__bases__:
                continue
            file_path = os.path.join(producers_path, file_name)
            Producers.append(Producer)
            hashes += hash_file(file_path)
    del file_name

    return Producers

def get_exec_order(producers):
    graph = DependencyGraph(producers)
    return graph.toposort()

def get_all_requirements(exec_order, producers):
    requirements = []
    for i, producer in enumerate(producers):
        if i in exec_order:
            requirements += producer.full_requires
    return requirements

def save(obj, name, path):

    # How to save matplotlib plots
    if type(obj) == Plot:
        return obj.save(path, name)

    # If there is no special rule, just pickle
    file_name = os.path.join(path, name + ".pkl")
    mkdir(os.path.dirname(file_name))
    with open( file_name, "wb" ) as f:
        pickle.dump(obj, f)
    return os.path.getsize(file_name)

import re

class ProductMatch(object):

    def __init__(self, product, producer):

        regex = re.sub('<[^<>]*>', '[^/]*', producer.product)
        match = re.match(".*"+regex+"$", product)

        if match is None:
            self.group = None
            self.subs  = {}
            self.score = 0
            return

        depth = producer.product.count("/")

        # The matching pattern
        self.group = "/".join(match.group().split("/")[-depth-1:])
        # The "matching depth". Products which match deeper are resolving ambiguities.
        self.score = self.group.count("/") + 1

        # The substitutions for the template specialization
        self.subs = {}
        for t, s in zip(producer.product.split("/"), self.group.split("/")):
            if t != s:
                self.subs[t] = s

import numpy as np

def get_required_producers(product, Producers, out_dir):

    if '*' in product:
        producers = []
        for p in expand_wildcard(product, out_dir):
            producers += get_required_producers(p[1:], Producers, out_dir)
        return producers

    n = len(Producers)
    matches = list(map(lambda P : ProductMatch(product, P), Producers))
    # Penalize matching depth score with number of template specializations
    # to give priority to full specializations.
    scores = [m.score - len(m.subs)/100. for m in matches]
    if max(scores) == 0: return []
    i = np.argmax(scores)

    working_dir = product[:-len(matches[i].group)]
    producers = [Producers[i](matches[i].subs, working_dir)]

    for i, req in enumerate(producers[0].requires):

        if "*" in req:
            producers[0].requires[i] = expand_wildcard(req, out_dir)

        producers += get_required_producers(os.path.join(working_dir, req), Producers, out_dir)

    return producers

def geek_run(config):

    try:
        # Try to open the file to see if it's a valid file path
        with open(config, 'r') as f:
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
    out_dir   = config.out_dir   if hasattr(config, "out_dir")   else "output"

    # Create list of dataset instances from configuration tuples
    datasets = [Dataset(*args) for args in config.datasets]

    # Create the output dir structure
    os.system("rm -rf "+out_dir) # Delete previous output to not confuse glob
    for ds in datasets: mkdir(os.path.join(out_dir, "."+ds.geeksw_path))

    Producers = get_producer_classes(producers_path)
    producers = []

    print(target_products)

    for t in target_products: producers += get_required_producers(t[1:], Producers, out_dir)
    producers = list(set(producers))

    print("Producers:")
    for i, producer in enumerate(producers):
        print("[{0}]".format(i), *producer.requires, "->", producer.product)

    exec_order = get_exec_order(producers)

    record = {}

    # Loop over producers needed to get to the desired output products
    for i, ip in enumerate(exec_order):

        pname = producers[ip].full_product
        print("Producing", pname, "...")

        working_dir = producers[ip].working_dir
        inputs = {}
        for req in producers[ip].requires:
            inputs[req] = record[os.path.join(working_dir, req)]

        product = producers[ip].run(inputs)
        record[pname] = product

        if producers[ip].cache:
            size = save(product, pname, cache_dir)
            print("Caching product {0}: {1}".format(pname, humanbytes(size)))

        if pname in target_products:
            size = save(product, pname, out_dir)
            print("Saving output {0}: {1}".format(pname, humanbytes(size)))

        requirements = get_all_requirements(exec_order[i+1:], producers)
        for key in list(record.keys()):
            if key not in requirements:
                del record[key]

    return record
