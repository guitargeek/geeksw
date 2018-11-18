import os
import importlib
import hashlib

def hash_file(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

producer_path = "producers"

producer_infos = {}

for file_name in os.listdir(producer_path):
    if file_name == '__init__.py' or file_name[-3:] != '.py':
        continue
    module = importlib.import_module("producers."+file_name[:-3])
    name = module.__name__.split(".")[-1]
    if name in dir(module):
        Producer = getattr(module, name)
        file_path = os.path.join(producer_path, file_name)
        producer_infos[name] = {
                "produces" : Producer.produces,
                "requires"  : Producer.requires,
                "hash" : hash_file(file_path),
                "class" : Producer,
                }
        print(producer_infos[name])
del file_name

# for name in dir(producers):
    # if "__" in name:
        # continue

def get_dependency_graph(producer_infos):
    requires_dict = {}
    for name, info in producer_infos.items():
        for req in info["requires"]:
            if req not in requires_dict:
                requires_dict[req] = []
            requires_dict[req] += [name]

    graph = {}
    for name, info in producer_infos.items():
        graph[name] = []
        for prod in info["produces"]:
            if not prod in requires_dict: continue
            for other in requires_dict[prod]:
                graph[name] += [other]

    return graph

def kahn_topsort(graph):
    from collections import deque

    in_degree = { u : 0 for u in graph }     # determine in-degree 
    for u in graph:                          # of each node
        for v in graph[u]:
            in_degree[v] += 1
 
    Q = deque()                 # collect nodes with zero in-degree
    for u in in_degree:
        if in_degree[u] == 0:
            Q.appendleft(u)
 
    L = []     # list for order of nodes
     
    while Q:                
        u = Q.pop()          # choose node of zero in-degree
        L.append(u)          # and 'remove' it from graph
        for v in graph[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                Q.appendleft(v)
 
    if len(L) == len(graph):
        return L
    else:                    # if there is a cycle,  
        print("Circular dependence! Will not do anything.")
        return []            # then return an empty list

def get_exec_order(producer_infos):
    graph = get_dependency_graph(producer_infos)
    return kahn_topsort(graph)

exec_order = get_exec_order(producer_infos)

print(exec_order)

record = {}

def get_all_requirements(producer_list, producer_infos):
    requirements = []
    for producer in producer_list:
        requirements += producer_infos[producer]["requires"]
    return requirements

for i_producer, name in enumerate(exec_order):
    print("Executing module "+name+"...")
    Producer = producer_infos[name]["class"]
    producer = Producer()
    producer.run(record)
    print(record)
    requirements = get_all_requirements(exec_order[i_producer+1:], producer_infos)
    keys = list(record)
    for key in keys:
        if key not in requirements:
            del record[key]

print(record)
