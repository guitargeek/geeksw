import functools

def produces(*product_names):

    if len(product_names) > 1:
        raise ValueError("Producers functions with more than one product not supported yet!")
    product_name = product_names[0]

    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            return func(**inputs)
        setattr(producer_func, "product", product_name)
        if not hasattr(producer_func, "requirements"):
            setattr(producer_func, "requirements", {})
        is_template = "<" in product_name or ">" in product_name
        setattr(producer_func, "_is_template", is_template)
        return producer_func
    return wrapper

def requires(**requirements):
    def wrapper(func):
        @functools.wraps(func)
        def producer_func(**inputs):
            return func(**inputs)
        setattr(producer_func, "requirements", requirements)
        return producer_func
    return wrapper
