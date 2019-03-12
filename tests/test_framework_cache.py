import unittest
import uproot
import awkward
import pandas as pd
import numpy as np
import shutil
import geeksw.framework as fwk
from geeksw.data_formats import Cutflow


np.random.seed(42)
n = 100
a = np.random.normal(size=n)

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
    df = pd.DataFrame(dict(x=a))
    return df


@fwk.one_producer("data", stream=True)
@fwk.consumes(token="data_token")
def make_data_frame_stream(token):
    df = pd.DataFrame(dict(x=a))
    return [df, df, df]


@fwk.one_producer("data")
@fwk.consumes(token="data_token")
def make_array(token):
    return a[:]


@fwk.one_producer("data")
@fwk.consumes(token="data_token")
def make_jagged(token):
    return awkward.JaggedArray([0], [n], a[:])


@fwk.one_producer("data")
@fwk.consumes(token="data_token")
def make_scalar(token):
    return a[0]


@fwk.one_producer("data")
@fwk.consumes(token="data_token")
def make_cutflow(token):
    cutflow = Cutflow.frommasks([a > -0.1, a > 0.1], ["cut0", "cut1"])
    print(cutflow)
    return cutflow


@fwk.one_producer("data", cache=False)
@fwk.consumes(token="data_token")
def make_scalar_nocache(token):
    return a[0]


def _test_cache(self, producers, test_disabeled=False, data_transf=lambda a: a, a_transf=lambda a: a, cache_time=None):

    # Make sure there is no cache so far
    try:
        shutil.rmtree(cache_dir)
    except:
        pass

    if cache_time is None:
        cache_time = 0.0

    a[:] = np.random.normal(size=n)

    record = fwk.produce(
        products=["/data"], producers=producers, max_workers=32, cache_time=cache_time, cache_dir=cache_dir
    )
    np.testing.assert_array_almost_equal(data_transf(record["data"]), a_transf(a))

    a[:] = np.random.normal(size=n) + 1.0
    record = fwk.produce(products=["/data"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir)

    shutil.rmtree(cache_dir)

    if test_disabeled:
        np.testing.assert_array_almost_equal(data_transf(record["data"]), a_transf(a))
    else:
        if isinstance(record["data"], Cutflow):
            self.assertNotEqual(data_transf(record["data"]), a_transf(a))
        else:
            assert_array_notequal(data_transf(record["data"]), a_transf(a))


class Test(unittest.TestCase):

    # test DataFrame
    test_framework_cache_dataframe = lambda self: _test_cache(
        self, [open_data, make_data_frame], data_transf=lambda data: data["x"].values
    )

    # test nd.array
    test_framework_cache_array = lambda self: _test_cache(self, [open_data, make_array])

    # test JaggedArray
    test_framework_cache_jagged = lambda self: _test_cache(
        self, [open_data, make_jagged], data_transf=lambda data: data.flatten()
    )

    # test scalar
    test_framework_cache_scalar = lambda self: _test_cache(self, [open_data, make_scalar], a_transf=lambda a: a[0])

    # test cutflow
    test_framework_cache_cutflow = lambda self: _test_cache(
        self,
        [open_data, make_cutflow],
        data_transf=lambda cf: cf.efficiency,
        a_transf=lambda a: Cutflow.frommasks([a > -0.1, a > 0.1], ["cut0", "cut1"]).efficiency,
    )

    # test disabeling cache by setting high timeout
    test_framework_cache_notimeout = lambda self: _test_cache(
        self, [open_data, make_scalar], a_transf=lambda a: a[0], test_disabeled=True, cache_time=1.0
    )

    # test diabling cache by doing so explicitely in the producer
    test_framework_cache_disabeled = lambda self: _test_cache(
        self, [open_data, make_scalar_nocache], a_transf=lambda a: a[0], test_disabeled=True
    )

    # Test caching of StreamLists
    test_framework_cache_dataframe_stream = lambda self: _test_cache(
        self, [open_data, make_data_frame_stream], data_transf=lambda data: data[0]["x"].values
    )


if __name__ == "__main__":

    unittest.main(verbosity=2)
