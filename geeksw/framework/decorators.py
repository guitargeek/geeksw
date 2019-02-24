import functools
from .futures import MultiFuture
from concurrent.futures import ThreadPoolExecutor


def produces(*product_names):

    if len(product_names) > 1:
        raise ValueError("Producers functions with more than one product not supported yet!")
    product_name = product_names[0]

    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            return func(**inputs)

        # For the hash, maybe get inspired by Parsl
        producer_func.product = product_name
        is_template = "<" in product_name or ">" in product_name
        producer_func.is_template = is_template
        if not hasattr(producer_func, "requirements"):
            producer_func.requirements = {}
        return producer_func
    return wrapper


def consumes(**requirements):
    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            return func(**inputs)

        # For the hash, maybe get inspired by Parsl
        producer_func.requirements = requirements
        return producer_func
    return wrapper


def identity_wrapper(func):
    @functools.wraps(func)
    def producer_func(**inputs):
        return func(**inputs)
    return producer_func


# Nothing special for now, it's the users responsability to get the output in the right shape
global_to_stream = identity_wrapper
global_to_global = identity_wrapper


def stream_to_global(func):
    @functools.wraps(func)
    def producer_func(**inputs):
        for v in inputs.values():
            if hasattr(v, "__len__"):
                n = len(v)
                break
        streamed_inputs = [{k : v[i] for k, v in inputs.items() if k != "meta"} for i in range(n)]
        if "meta" in inputs.keys():
            for i in range(len(streamed_inputs)):
                streamed_inputs[i]["meta"] = inputs["meta"]
        executor = ThreadPoolExecutor(max_workers=32)
        return MultiFuture([executor.submit(func, **streamed_inputs[i]) for i in range(n)]).result()

    return producer_func


def stream_to_stream(func):
    @functools.wraps(func)
    def producer_func(**inputs):
        for v in inputs.values():
            if hasattr(v, "__len__"):
                n = len(v)
                break
        streamed_inputs = [{k : v[i] for k, v in inputs.items() if k != "meta"} for i in range(n)]
        if "meta" in inputs.keys():
            for i in range(len(streamed_inputs)):
                streamed_inputs[i]["meta"] = inputs["meta"]
        executor = ThreadPoolExecutor(max_workers=32)
        return MultiFuture([executor.submit(func, **streamed_inputs[i]) for i in range(n)]).result()

    return producer_func
