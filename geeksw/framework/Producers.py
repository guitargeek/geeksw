import os.path
import glob
import itertools


def expand_wildcard(product, datasets):
    if not "*" in product:
        return [product]
    return [product.replace("*", ds) for ds in datasets]


def replace_from_dict(s, subs):
    for t in subs:
        s = s.replace(t, subs[t])
    return s


class ProducerWrapper(object):

    def __init__(self, func, subs, working_dir, datasets):
        product = replace_from_dict(func.product, subs)
        requirements = {k : replace_from_dict(v, subs) for k, v in func.requirements.items()}

        self.description = " ".join(list(requirements.values()) + ["->", product])

        self.subs = subs
        self.product = working_dir + product

        self.requirements = {k : expand_wildcard(working_dir + v, datasets) for k, v in requirements.items()}
        self.flattened_requirements = [y for x in self.requirements.values() for y in x]

        self.func = func

    def run(self, record):
        inputs = {}
        for k, req in self.requirements.items():
            if len(req) > 1:
                inputs[k] = [(x, record[x]) for x in req]
            else:
                inputs[k] = record[req[0]]

        if self.func.is_template:
            for k in inputs:
                inputs[k].subs = self.subs

        return self.func(**inputs)

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
        return hash(self.product)
