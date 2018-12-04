class DependencyGraph(object):

    def __init__(self, producer_infos, target_products=None):
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

        # If target_products is None, which means produce everything, we are done.
        self.graph = dict(graph)
        self.producer_infos = dict(producer_infos)

        if target_products is None:
            return

        # Otherwise we want to prune the graph such that only products needed to
        # produce our targets are calculated
        self.prune(target_products)

    def prune(self, target_products):
        output_producers = []
        for name, info in self.producer_infos.items():
            for prod in info["produces"]:
                if prod in target_products:
                    output_producers.append(name)

        pruned = True
        while(pruned):
            pruned = False
            for name, lst in self.graph.items():
                if not name in output_producers and lst == []:
                    self.remove(name)
                    pruned = True

    def remove(self, name):
        """ Remove an element from a graph and return new graph.
        """
        # make a copy
        graph = dict(self.graph)
        graph.pop(name, None)
        for key, lst in graph.items():
            if name in lst: lst.remove(name)

        self.graph = graph

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
