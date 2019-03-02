import functools
from concurrent.futures import ThreadPoolExecutor
from ..utils.core import concatenate
from .futures import MultiFuture
from .ProducerWrapper import ExpandedProduct


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


def consumes(**requirements):
    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            return func(**inputs)

        # For the hash, maybe get inspired by Parsl
        producer_func.requirements = requirements
        return producer_func

    return wrapper


def one_producer(product_names, stream=False):
    if isinstance(product_names, list) and len(product_names) > 1:
        raise ValueError("Producers functions with more than one product not supported yet!")
    product_name = product_names

    def one_wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            for k1, product in inputs.items():
                if isinstance(product, StreamList):
                    inputs[k1] = product.aggregate()
                if isinstance(product, ExpandedProduct):
                    for k2, subproduct in product.items():
                        if isinstance(subproduct, StreamList):
                            inputs[k1][k2] = subproduct.aggregate()

            if stream:
                return StreamList(func(**inputs))
            return func(**inputs)

        producer_func.product = product_name
        is_template = "<" in product_name or ">" in product_name
        producer_func.is_template = is_template
        if not hasattr(producer_func, "requirements"):
            producer_func.requirements = {}
        return producer_func

    return one_wrapper


def stream_producer(*product_names):
    if len(product_names) > 1:
        raise ValueError("Producers functions with more than one product not supported yet!")
    product_name = product_names[0]

    def stream_wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            stream_list_lengths = set([len(v) for v in inputs.values() if isinstance(v, StreamList)])

            if len(stream_list_lengths) == 0:
                # in this case, it might as well be a "one" producer
                return func(**inputs)
            elif len(stream_list_lengths) > 1:
                raise ValueError("A stream produces can't take multiple stream inputs of different lengths!")

            n = stream_list_lengths.pop()

            sinputs = [dict() for k in range(n)]

            for k, v in inputs.items():
                isstream = isinstance(v, StreamList)
                for i in range(n):
                    print(i, k)
                    sinputs[i][k] = v[i] if isstream else v

            with ThreadPoolExecutor(max_workers=32) as executor:
                results = MultiFuture([executor.submit(func, **sinputs[i]) for i in range(n)]).result()
            return StreamList(results)

        producer_func.product = product_name
        is_template = "<" in product_name or ">" in product_name
        producer_func.is_template = is_template
        if not hasattr(producer_func, "requirements"):
            producer_func.requirements = {}
        return producer_func

    return stream_wrapper
