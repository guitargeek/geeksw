import hashlib

def hash_file(path):
    hasher = hashlib.md5()
    with open(path, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

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
