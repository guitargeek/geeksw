import functools
from parsl.app.app import python_app
from .futures_helpers import MultiFuture


def produces(*product_names):

    if len(product_names) > 1:
        raise ValueError("Producers functions with more than one product not supported yet!")
    product_name = product_names[0]

    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            return func(**inputs)

        if not hasattr(producer_func, "func_hash"):
            producer_func = python_app(producer_func)

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

        if not hasattr(producer_func, "func_hash"):
            producer_func = python_app(producer_func)

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


def stream_to_global(merger_func):
    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            n = len(next(iter(inputs.values())))
            streamed_inputs = [{k : v[i] for k, v in inputs.items() if k != "meta"} for i in range(n)]
            if "meta" in inputs.keys():
                for i in streamed_inputs:
                    streamed_inputs["meta"] = inputs["meta"]
            return MultiFuture([func(**streamed_inputs[i]) for i in range(n)], merger=merger_func)

        return producer_func
    return wrapper


def stream_to_stream(func):
    @functools.wraps(func)
    def producer_func(**inputs):
        n = len(next(iter(inputs.values())))
        streamed_inputs = [{k : v[i] for k, v in inputs.items()} for i in range(n)]
        return MultiFuture([func(**streamed_inputs[i]) for i in range(n)])

    return producer_func
