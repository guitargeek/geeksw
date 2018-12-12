class Producer(object):

    cache = False

    def __init__(self, subs, working_dir):

        def replace_from_dict(s, subs):
            for t in subs:
                s = s.replace(t, subs[t])
            return s

        self.product = replace_from_dict(self.product, subs)
        self.requires = [replace_from_dict(req, subs) for req in self.requires]

        self.working_dir = working_dir

    def __eq__(self, other):
        """ Check if producer has same template specialization.
        """
        if type(self) != type(other):
            return False
        return self.product == other.product and self.working_dir == other.working_dir

    def __hash__(self):
        """ Should be some collision free hash function to spot duplicate producers.
            Used in set().
        """
        return hash(self.working_dir + self.product)

