import functools
from parsl.app.app import python_app

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


def set_producer_type(producer_type):
    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            return func(**inputs)

        if not hasattr(producer_func, "producer_type"):
            producer_func.producer_type = producer_type

        return producer_func
    return wrapper


global_to_stream = set_producer_type("global_to_stream")
global_to_global = set_producer_type("global_to_global")
stream_to_stream = set_producer_type("stream_to_stream")
stream_to_global = set_producer_type("stream_to_global")
