class Producer(object):

    cache = True

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
        return hash(self.product)

