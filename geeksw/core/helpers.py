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

def humanbytes(B):
   'Return the given bytes as a human friendly KB, MB, GB, or TB string'
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0:.0f} {1}'.format(B,'Byte')
   elif KB <= B < MB:
      return '{0:.1f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.1f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.1f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.1f} TB'.format(B/TB)
