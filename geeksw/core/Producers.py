import os.path
import glob
import itertools

def path_product(p1, p2):
    return [os.path.join(*x) for x in itertools.product(p1, p2)]

def expand_wildcard(product, out_dir):
    if not "*" in product:
        return [product]
    i = product[::-1].find("*")
    wildcard_expr = os.path.join(out_dir, product[:-i])
    rest = product[-i:]
    return [path[len(out_dir)+1:] + rest for path in glob.glob(wildcard_expr)]

class Producer(object):

    requires = []
    cache = False

    def expand_full_requires(self, flatten=False):
        expanded = [expand_wildcard(req, self.out_dir) for req in self.full_requires]
        if flatten:
            return [y for x in expanded for y in x]
        return expanded

    def __init__(self, subs, working_dir, out_dir):

        def replace_from_dict(s, subs):
            for t in subs:
                s = s.replace(t, subs[t])
            return s

        self.subs = subs

        self.product = replace_from_dict(self.product, subs)
        self.requires = [replace_from_dict(req, subs) for req in self.requires]

        self.working_dir = working_dir
        self.out_dir = out_dir

        self.full_product = self.working_dir + self.product
        self.full_requires = [self.working_dir + req for req in self.requires]

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

