import numpy as np

class Producer(object):

    def __init__(self, subs):

        def replace_from_dict(s, subs):
            for t in subs:
                s = s.replace(t, subs[t])
            return s

        self.product = replace_from_dict(self.product, subs)
        self.requires = [replace_from_dict(req, subs) for req in self.requires]

    def __eq__(self, other):
        """ Check if producer has same template specialization.
        """
        if type(self) != type(other):
            return False
        return self.product == other.product

    def __hash__(self):
        """ Should be some collision free hash function to spot duplicate producers.
            Used in set().
        """
        return abs(id(self) + hash(self.product))

class Generator(Producer):

    product = "<distribution>"
    requires = []

    def run(self, inputs):
        if self.product == "data/uniform":
            return np.random.uniform(0,1,1000)
        if self.product == "data/normal":
            return np.random.normal(size=1000)
        if self.product == "data/exponential":
            return np.random.uniform(scale=1.0, size=1000)
        else:
            return np.zeros(10)

import matplotlib.pyplot as plt

class Plotter(Producer):

    product = "plot"
    requires = ["data/uniform", "data/normal", "data/exponential"]

    def run(self, inputs):
        plt.figure()
        plt.plot(inputs["data/uniform"])
        plt.plot(inputs["data/normal"])
        plt.plot(inputs["data/exponential"])
        plt.show()

import re

class ProductMatch(object):

    def __init__(self, product, producer):

        regex = re.sub('<[^<>]*>', '[^/]*', producer.product)
        match = re.match(regex+"$", product)

        if match is None:
            self.group = None
            self.subs  = {}
            self.score = 0
            return

        # The matching pattern
        self.group = match.group()
        # The "matching depth". Products which match deeper are resolving ambiguities.
        self.score = self.group.count("/") + 1

        # The substitutions for the template specialization
        self.subs = {}
        for t, s in zip(producer.product.split("/"), self.group.split("/")):
            if t != s:
                self.subs[t] = s

Producers = [
             Generator,
             Plotter,
            ]

targets = ["plot"]

def get_required_producer(product, Producers):
    n = len(Producers)
    matches = list(map(lambda P : ProductMatch(product, P), Producers))
    # Penalize matching depth score with number of template specializations
    # to give priority to full specializations.
    scores = [m.score - len(m.subs)/100. for m in matches]
    if max(scores) == 0: return []
    i = np.argmax(scores)
    producers = [Producers[i](matches[i].subs)]
    for req in producers[0].requires:
        producers += get_required_producer(req, Producers)
    return producers

producers = []

for t in targets: producers += get_required_producer(t, Producers)
producers = set(producers)

for producer in producers:
    for req in producer.requires:
        print(req, producer.product)

# print(match)
# record = {}
# producer.run(record)
