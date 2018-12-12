import numpy as np

class Producer(object):

    def __init__(self, subs):

        def replace_from_dict(s, subs):
            for t in subs:
                s = s.replace(t, subs[t])
            return s

        self.product = replace_from_dict(self.product, subs)
        self.requires = [replace_from_dict(req, subs) for req in self.requires]

class Generator(Producer):

    product = "data/<distribution>"
    requires = []

    def run(self, inputs):
        if self.product == "uniform":
            return np.random.uniform(0,1,1000)
        if self.product == "normal":
            return np.random.normal(size=1000)
        if self.product == "exponential":
            return np.random.uniform(scale=1.0, size=1000)
        else:
            return np.zeros(10)

import matplotlib.pyplot as plt

class Plotter(Producer):

    product = "plot"
    requires = ["data/uniform", "data/normal", "data/exponential"]

    def run(self, inputs):
        plt.figure()
        plt.plot(inputs["uniform"])
        plt.plot(inputs["normal"])
        plt.plot(inputs["exponential"])
        plt.show()

import re

class ProductMatch(object):

    def __init__(self, product, producer):

        regex = re.sub('<[^<>]*>', '[^/]*', producer.product)
        match = re.match(regex+"$", product)

        if match is None:
            self.group = None
            self.subs  = None
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

producers = [
             Generator,
             Plotter,
            ]

b = "plot"

# def get_required_producer(product, producers):
score = 0
match = None
producer = None
for p in producers:
    new_match = ProductMatch(b, p)
    if new_match.score > score:
        match = new_match
        score = match.score
        producer = p(match.subs)



print(match)
record = {}
producer.run(record)
