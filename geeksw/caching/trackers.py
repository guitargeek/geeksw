import time


def iterable(a):
    try:
        iterator = iter(a)
        return True
    except TypeError:
        return False


def timer(f):
    start_time = time.time()
    result = f()
    return time.time() - start_time, result


class Handle(object):
    pass


def untrack(x):
    if issubclass(type(x), Handle):
        return x.product
    else:
        return x


def FHashCacheTracker(cache=dict(), strict=True, verbosity=0):

    from functools import wraps
    import inspect

    def log(s):
        if verbosity >= 1:
            print(s)

    class HashHandle(Handle):
        def __init__(self, product, hash):
            self._product = product
            self._hash = hash

        @property
        def product(self):
            return self._product

        def __hash__(self):
            return self._hash

        def __repr__(self):
            return "<HashHandle " + self._product.__repr__() + ">"

    def unwrap_handles(handles, strict=True):
        if not iterable(handles):
            handles = (handles,)
        products = []
        combined_hash = 0
        for h in handles:
            if isinstance(h, HashHandle):
                products.append(h.product)
            else:
                products.append(h)
            try:
                combined_hash ^= hash(h)
            except TypeError:
                if strict:
                    raise TypeError("with strict=True, you can only unwrap handles or other hashable types")

        return products, combined_hash

    def tracks_decorator(func):
        source = inspect.getsource(func)
        source_hash = hash(source)

        @wraps(func)
        def func_wrapper(*handle_args, **handle_kwargs):

            args, args_hash = tuple(), 0
            kwargs, kwargs_hash = dict(), 0

            if handle_args:
                args, args_hash = unwrap_handles(handle_args)

            if handle_kwargs:
                kwargs_keys, handle_kwargs_values = zip(*[(k, v) for k, v in handle_kwargs.items()])
                kwargs_values, kwargs_hash = unwrap_handles(handle_kwargs_values)
                kwargs = dict(zip(kwargs_keys, kwargs_values))

            output_hash = args_hash ^ kwargs_hash ^ source_hash

            if output_hash in cache:
                elapsed_time, output = timer(lambda: cache[output_hash])
                log(func.__name__ + ": loading result from cache took {0:.2f} s".format(elapsed_time))
                return HashHandle(output, output_hash)

            elapsed_time, output = timer(lambda: func(*args, **kwargs))

            def c():
                cache[output_hash] = output

            caching_time, _ = timer(c)
            log(
                func.__name__
                + ": calculating result took {0:.2f} s, caching {1:.2f} s".format(elapsed_time, caching_time)
            )

            return HashHandle(output, output_hash)

        return func_wrapper

    return tracks_decorator
