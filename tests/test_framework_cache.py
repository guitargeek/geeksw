import unittest
import geeksw.framework as fwk
import uproot
import awkward
import pandas as pd
import numpy as np
import shutil

np.random.seed(42)
a = np.random.normal(size=10)

cache_dir = ".test_framework_cache"


def assert_array_notequal(x, y):
    try:
        np.testing.assert_array_almost_equal(x, y)
        return False
    except:
        True


@fwk.one_producer("data_token", cache=False)
def open_data():
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return True


@fwk.one_producer("data")
@fwk.consumes(token="data_token")
def make_data_frame(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    df = pd.DataFrame(dict(x=a))
    return df


@fwk.one_producer("data", stream=True)
@fwk.consumes(token="data_token")
def make_data_frame_stream(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    df = pd.DataFrame(dict(x=a))
    return [df, df, df]


@fwk.one_producer("data")
@fwk.consumes(token="data_token")
def make_array(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return a[:]


@fwk.one_producer("data")
@fwk.consumes(token="data_token")
def make_jagged(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return awkward.JaggedArray([0], [10], a[:])


@fwk.one_producer("data")
@fwk.consumes(token="data_token")
def make_scalar(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return a[0]


@fwk.one_producer("data", cache=False)
@fwk.consumes(token="data_token")
def make_scalar_nocache(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return a[0]


def _test_cache(self, producers, test_disabeled=False, data_transf=lambda a: a, a_transf=lambda a: a, cache_time=None):

    # Make sure there is no cache so far
    try:
        shutil.rmtree(cache_dir)
    except FileNotFoundError:
        pass

    if cache_time is None:
        cache_time = 0.0

    record = fwk.produce(
        products=["/data"], producers=producers, max_workers=32, cache_time=cache_time, cache_dir=cache_dir
    )
    np.testing.assert_array_almost_equal(data_transf(record["data"]), a_transf(a))

    a[:] = np.random.normal(size=10)
    record = fwk.produce(products=["/data"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir)
    if test_disabeled:
        np.testing.assert_array_almost_equal(data_transf(record["data"]), a_transf(a))
    else:
        assert_array_notequal(data_transf(record["data"]), a_transf(a))

    shutil.rmtree(cache_dir)


class Test(unittest.TestCase):

    test_framework_cache_dataframe = lambda self: _test_cache(
        self, [open_data, make_data_frame], data_transf=lambda data: data["x"].values
    )
    test_framework_cache_array = lambda self: _test_cache(self, [open_data, make_array])
    test_framework_cache_jagged = lambda self: _test_cache(
        self, [open_data, make_jagged], data_transf=lambda data: data.flatten()
    )
    test_framework_cache_scalar = lambda self: _test_cache(self, [open_data, make_scalar], a_transf=lambda a: a[0])
    test_framework_cache_notimeout = lambda self: _test_cache(
        self, [open_data, make_scalar], a_transf=lambda a: a[0], test_disabeled=True, cache_time=1.0
    )
    test_framework_cache_disabeled = lambda self: _test_cache(
        self, [open_data, make_scalar_nocache], a_transf=lambda a: a[0], test_disabeled=True
    )

    test_framework_cache_dataframe_stream = lambda self: _test_cache(
        self, [open_data, make_data_frame_stream], data_transf=lambda data: data[0]["x"].values
    )


if __name__ == "__main__":

    unittest.main(verbosity=2)
