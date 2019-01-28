import functools

def produces(*product_names):

    if len(product_names) > 1:
        raise ValueError("Producers functions with more than one product not supported yet!")
    product_name = product_names[0]

    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            return func(**inputs)
        producer_func.product = product_name
        is_template = "<" in product_name or ">" in product_name
        producer_func._is_template = is_template
        if not hasattr(producer_func, "_orig_code_hash"):
            producer_func._orig_code_hash = hash(func.__code__)
        return producer_func
    return wrapper

def consumes(**requirements):
    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            return func(**inputs)
        producer_func.requirements = requirements
        if not hasattr(producer_func, "_orig_code_hash"):
            producer_func._orig_code_hash = hash(func.__code__)
        return producer_func
    return wrapper
