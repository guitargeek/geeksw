import os
import importlib.util

from .helpers import *

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
                    "produces" : Producer.produces,
                    "requires"  : Producer.requires,
                    "hash" : hash_file(file_path),
                    "class" : Producer,
                    }
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

def geek_run(producers_path):
    record = {}
    producer_infos = get_producer_infos(producers_path)
    exec_order = get_exec_order(producer_infos)

    for i_producer, name in enumerate(exec_order):
        print("Executing module "+name+"...")
        Producer = producer_infos[name]["class"]
        producer = Producer()
        producer.run(record)
        requirements = get_all_requirements(exec_order[i_producer+1:], producer_infos)
        keys = list(record)
        for key in keys:
            if key not in requirements:
                del record[key]
    return record

