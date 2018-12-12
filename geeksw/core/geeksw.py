import sys
import os
import pickle
import inspect

from .helpers import *
from .DependencyGraph import DependencyGraph
from .Plot import Plot
from .Record import Record
from .Producers import SingleDatasetProducer

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

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


def get_producer_infos(producers_path):
    producer_infos = {}

    for file_name in os.listdir(producers_path):
        if file_name == '__init__.py' or file_name[-3:] != '.py':
            continue
        name = file_name[:-3]
        module = load_module(name, os.path.join(producers_path,file_name))
        for item in dir(module):
            Producer = getattr(module, item)
            if not inspect.isclass(Producer) or not issubclass(Producer, SingleDatasetProducer):
                continue
            file_path = os.path.join(producers_path, file_name)
            producer_infos[item] = {
                    "produces"  : [],
                    "requires"  : [],
                    "hash"      : hash_file(file_path),
                    "class"     : Producer,
                    "cache"     : True,
                    }
            for attr in ["produces", "requires", "cache"]:
                if hasattr(Producer, attr):
                    producer_infos[item][attr] = getattr(Producer, attr)
    del file_name

    return producer_infos

def get_exec_order(producer_infos, target_products):
    graph = DependencyGraph(producer_infos, target_products)
    return graph.toposort()

def get_all_requirements(producer_list, producer_infos):
    requirements = []
    for producer in producer_list:
        requirements += producer_infos[producer]["requires"]
    return requirements

def save(obj, name, path):

    # How to save matplotlib plots
    if type(obj) == Plot:
        return obj.save(path, name)

    # If there is no special rule, just pickle
    file_name = os.path.join(path, "pkl", name + ".pkl")
    mkdir(os.path.dirname(file_name))
    with open( file_name, "wb" ) as f:
        pickle.dump(obj, f)
    return os.path.getsize(file_name)

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

    out_dir_base = "output"
    cache_dir_base = "cache"

    if hasattr(config, "cache_dir"): out_dir_base = config.cache_dir
    if hasattr(config, "out_dir")  : out_dir_base = config.out_dir

    producer_infos = get_producer_infos(producers_path)

    exec_order = get_exec_order(producer_infos, target_products)

    records = {}

    # Loop over all datasets
    for  dataset in config.datasets:
        print("Processing dataset "+dataset[1]+"...")

        record = Record()
        out_dir   = os.path.join(out_dir_base, dataset[1])
        cache_dir = os.path.join(cache_dir_base, dataset[1])

        # Loop over producers needed to get to the desired output products
        for i_producer, name in enumerate(exec_order):

            print("Executing module "+name+"...")

            Producer = producer_infos[name]["class"]
            producer = Producer()
            producer.run(dataset, record)

            if producer_infos[name]["cache"]:
                for p in producer_infos[name]["produces"]:
                    size = save(record.get(p), p, cache_dir)
                    print("Caching product {0}: {1}".format(p, humanbytes(size)))

            for p in producer_infos[name]["produces"]:
                if p in target_products:
                    size = save(record.get(p), p, out_dir)
                    print("Saving output {0}: {1}".format(p, humanbytes(size)))

            requirements = get_all_requirements(exec_order[i_producer+1:], producer_infos)
            keys = record.to_list()
            for key in keys:
                if key not in requirements:
                    record.delete(key)

        records[dataset[1]] = record

    return records
