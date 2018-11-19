import os
import importlib.util
import pickle

from .helpers import *
import geeksw.plotting

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_producer_infos(producers_path):
    producer_infos = {}

    for file_name in os.listdir(producers_path):
        if file_name == '__init__.py' or file_name[-3:] != '.py':
            continue
        name = file_name[:-3]
        spec = importlib.util.spec_from_file_location("module.name", os.path.join(producers_path,file_name))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if name in dir(module):
            Producer = getattr(module, name)
            file_path = os.path.join(producers_path, file_name)
            producer_infos[name] = {
                    "produces"  : [],
                    "requires"  : [],
                    "outputs"   : [],
                    "hash"      : hash_file(file_path),
                    "class"     : Producer,
                    }
            for attr in ["produces", "requires", "outputs"]:
                if hasattr(Producer, attr):
                    producer_infos[name][attr] = getattr(Producer, attr)
    del file_name

    return producer_infos

def get_exec_order(producer_infos):
    graph = get_dependency_graph(producer_infos)
    return kahn_topsort(graph)

def get_all_requirements(producer_list, producer_infos):
    requirements = []
    for producer in producer_list:
        requirements += producer_infos[producer]["requires"]
    return requirements

def save(obj, name, path):

    # How to save matplotlib plots
    if type(obj) == geeksw.plotting.wrapper.Plot:
        return obj.save(path, name)

    # If there is no special rule, just pickle
    file_name = os.path.join(path, name + ".pkl")
    with open( file_name, "wb" ) as f:
        pickle.dump(obj, f)
    return os.path.getsize(file_name)

def geek_run(producers_path):
    record = {}
    producer_infos = get_producer_infos(producers_path)
    exec_order = get_exec_order(producer_infos)

    # Set up the cache where products will be stored
    cache_dir = "cache"
    out_dir = "out"

    mkdir(cache_dir)
    mkdir(out_dir)
    mkdir(os.path.join(out_dir, "plots"))
    mkdir(os.path.join(out_dir, "plots/pkl"))
    mkdir(os.path.join(out_dir, "plots/png"))
    mkdir(os.path.join(out_dir, "plots/pdf"))

    for i_producer, name in enumerate(exec_order):

        print("Executing module "+name+"...")

        Producer = producer_infos[name]["class"]
        producer = Producer()
        producer.run(record)

        for p in producer_infos[name]["produces"]:
            size = save(record[p], p, cache_dir)
            print("Caching product {0}: {1}".format(p, humanbytes(size)))

        for p in producer_infos[name]["outputs"]:
            size = save(record[p], p, out_dir)
            print("Saving output {0}: {1}".format(p, humanbytes(size)))

        requirements = get_all_requirements(exec_order[i_producer+1:], producer_infos)
        keys = list(record)
        for key in keys:
            if key not in requirements:
                del record[key]

    return record
