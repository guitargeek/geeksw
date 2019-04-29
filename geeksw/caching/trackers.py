import time
from hashlib import md5

from .indexed_cache import IndexedCache


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


def FHashCacheTracker(cache_dir="~/.cache/geeksw", strict=True, verbosity=0):

    from functools import wraps
    import inspect

    cache = IndexedCache(path=cache_dir)

    def log(s):
        if verbosity >= 1:
            print(s)

    class SourceHandle(Handle):
        def __init__(self, product, source):
            self._product = product
            self._source = source

        @property
        def product(self):
            return self._product

        @property
        def source(self):
            return self._source

        def purge(self):
            """Purge corresponding product from cache in case something went wrong.
            """
            del cache[md5(self.source.encode("utf-8")).hexdigest()]

        def __repr__(self):
            return "<SourceHandle " + self._product.__repr__() + ">"

    def unwrap_handles(handles, strict=True):
        if not iterable(handles):
            handles = (handles,)
        products = []
        combined_source = ""
        for h in handles:
            if isinstance(h, SourceHandle):
                products.append(h.product)
                combined_source += h.source
            else:
                products.append(h)
                try:
                    combined_source += h
                except TypeError:
                    if strict:
                        raise TypeError("with strict=True, you can only use SourceHandles or strings to allow hashing")

        return products, combined_source

    def tracks_decorator(func):
        source = inspect.getsource(func)

        @wraps(func)
        def func_wrapper(*handle_args, **handle_kwargs):

            args, args_source = tuple(), ""
            kwargs, kwargs_source = dict(), ""

            if handle_args:
                args, args_source = unwrap_handles(handle_args)

            if handle_kwargs:
                kwargs_keys, handle_kwargs_values = zip(*[(k, v) for k, v in handle_kwargs.items()])
                kwargs_values, kwargs_source = unwrap_handles(handle_kwargs_values)
                kwargs = dict(zip(kwargs_keys, kwargs_values))

            output_source = args_source + kwargs_source + source
            output_hash = md5(output_source.encode("utf-8")).hexdigest()

            if output_hash in cache:
                elapsed_time, output = timer(lambda: cache[output_hash])
                info = " "
                if verbosity >= 1:
                    if type(output).__name__ == "ndarray":
                        info += "(ndarray of length {0})".format(len(output))
                    if type(output).__name__ == "JaggedArray":
                        info += "(JaggedArray of length {0}, flattened {1})".format(len(output), len(output.flatten()))
                log(func.__name__ + ": loading result from cache took {0:.2f} s".format(elapsed_time) + info)
                return SourceHandle(output, output_source)

            elapsed_time, output = timer(lambda: func(*args, **kwargs))

            def c():
                cache[output_hash] = output

            caching_time, _ = timer(c)
            log(
                func.__name__
                + ": calculating result took {0:.2f} s, caching {1:.2f} s".format(elapsed_time, caching_time)
            )

            return SourceHandle(output, output_source)

        return func_wrapper

    return tracks_decorator
