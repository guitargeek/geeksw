class DependencyGraph(object):

    def __init__(self, producers):

        requires_dict = {}
        for i, p in enumerate(producers):
            for req in p.requires:
                if req not in requires_dict:
                    requires_dict[req] = []
                requires_dict[req] += [i]

        graph = {}
        for i, p in enumerate(producers):
            graph[i] = []
            if not p.product in requires_dict: continue
            for other in requires_dict[p.product]:
                graph[i] += [other]

        self.graph = dict(graph)

    def toposort(self):
        """Kahn toposort.
        """
        from collections import deque
        graph = self.graph

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
