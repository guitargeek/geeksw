class MultiFuture(object):
    def __init__(self, futures, merger=None):

        self.merger = merger

        if hasattr(futures, "__len__"):
            self.futures = futures

        else:
            self.futures = [futures]

    def done(self):
        for f in self.futures:
            if not f.done():
                return False

        return True

    def result(self):
        if len(self.futures) == 1:
            return self.futures[0].result()

        if not self.merger is None:
            return self.merger([f.result() for f in self.futures])

        return [f.result() for f in self.futures]
