import unittest
import geeksw.framework as fwk
import uproot
import awkward
import pandas as pd
import numpy as np
import shutil

np.random.seed(42)
a = np.random.normal(size=10)


def assert_array_notequal(x, y):
    try:
        np.testing.assert_array_almost_equal(x, y)
        return False
    except:
        True


@fwk.one_producer("data_token")
def open_data():
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return True


@fwk.one_producer("data_frame")
@fwk.consumes(token="data_token")
def make_data_frame(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    df = pd.DataFrame(dict(x=a))
    return df


@fwk.one_producer("data_array")
@fwk.consumes(token="data_token")
def make_array(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return a[:]


@fwk.one_producer("data_jagged")
@fwk.consumes(token="data_token")
def make_jagged(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return awkward.JaggedArray([0], [10], a[:])


@fwk.one_producer("data_scalar")
@fwk.consumes(token="data_token")
def make_scalar(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return a[0]


class Test(unittest.TestCase):
    def test_framework_cache_dataframe(self):

        cache_dir = ".test_framework_cache"

        # Make sure there is no cache so far
        try:
            shutil.rmtree(cache_dir)
        except FileNotFoundError:
            pass

        producers = [open_data, make_data_frame]

        record = fwk.produce(
            products=["/data_frame"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir
        )
        np.testing.assert_array_almost_equal(record["data_frame"]["x"].values, a)

        a[:] = np.random.normal(size=10)
        record = fwk.produce(
            products=["/data_frame"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir
        )
        assert_array_notequal(record["data_frame"]["x"].values, a)

        shutil.rmtree(cache_dir)

    def test_framework_cache_array(self):

        cache_dir = ".test_framework_cache"

        # Make sure there is no cache so far
        try:
            shutil.rmtree(cache_dir)
        except FileNotFoundError:
            pass

        producers = [open_data, make_array]

        record = fwk.produce(
            products=["/data_array"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir
        )
        np.testing.assert_array_almost_equal(record["data_array"], a)

        a[:] = np.random.normal(size=10)
        record = fwk.produce(
            products=["/data_array"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir
        )
        assert_array_notequal(record["data_array"], a)

        shutil.rmtree(cache_dir)

    def test_framework_cache_jagged(self):

        cache_dir = ".test_framework_cache"

        # Make sure there is no cache so far
        try:
            shutil.rmtree(cache_dir)
        except FileNotFoundError:
            pass

        producers = [open_data, make_jagged]

        record = fwk.produce(
            products=["/data_jagged"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir
        )
        np.testing.assert_array_almost_equal(record["data_jagged"].flatten(), a.flatten())

        a[:] = np.random.normal(size=10)
        record = fwk.produce(
            products=["/data_jagged"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir
        )
        assert_array_notequal(record["data_jagged"].flatten(), a.flatten())

        shutil.rmtree(cache_dir)

    def test_framework_cache_scalar(self):

        cache_dir = ".test_framework_cache"

        # Make sure there is no cache so far
        try:
            shutil.rmtree(cache_dir)
        except FileNotFoundError:
            pass

        producers = [open_data, make_scalar]

        record = fwk.produce(
            products=["/data_scalar"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir
        )
        self.assertTrue(record["data_scalar"] == a[0])

        a[:] = np.random.normal(size=10)
        record = fwk.produce(
            products=["/data_scalar"], producers=producers, max_workers=32, cache_time=0.0, cache_dir=cache_dir
        )
        self.assertTrue(record["data_scalar"] != a[0])

        shutil.rmtree(cache_dir)


if __name__ == "__main__":

    unittest.main(verbosity=2)
