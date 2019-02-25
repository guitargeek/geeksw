import os.path
import glob
import itertools


def path_product(p1, p2):
    return [os.path.join(*x) for x in itertools.product(p1, p2)]


def expand_wildcard(product, datasets):
    if not "*" in product:
        return [product]
    return [product.replace("*", ds) for ds in datasets]


class Producer(object):

    requires = []
    cache = False

    def expand_full_requires(self, flatten=False):
        expanded = [expand_wildcard(req, self.datasets) for req in self.full_requires]
        if flatten:
            return [y for x in expanded for y in x]
        return expanded

    def __init__(self, func, subs, working_dir, datasets):

        self.product = func.product
        self.input_names = func.requirements.keys()
        self.requires = func.requirements.values()

        self.run = func

        def replace_from_dict(s, subs):
            for t in subs:
                s = s.replace(t, subs[t])
            return s

        self.subs = subs

        self.product = replace_from_dict(self.product, subs)
        self.requires = [replace_from_dict(req, subs) for req in self.requires]

        self.datasets = datasets

        self.full_product = working_dir + self.product
        self.full_requires = [working_dir + req for req in self.requires]
        self.full_requires_expanded = self.expand_full_requires()

    def __eq__(self, other):
        """ Check if producer has same template specialization.
        """
        if type(self) != type(other):
            return False
        return self.full_product == other.full_product

    def __hash__(self):
        """ Should be some collision free hash function to spot duplicate producers.
            Used in set().
        """
        return hash(self.full_product)
