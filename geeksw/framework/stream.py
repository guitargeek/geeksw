from ..utils.core import concatenate


class StreamList(list):
    """Class to replace a basic list for streamed products
    """

    def __init__(self, product):
        if isinstance(product, list):
            super(StreamList, self).__init__(product)
        else:
            super(StreamList, self).__init__([product])

        self._cached_aggregate = None

    def aggregate(self):
        if self._cached_aggregate is None:
            return concatenate(self)
        else:
            return self._cached_aggregate
