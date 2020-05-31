import unittest

import numpy as np

from geeksw.utils.data_loader_tools import make_data_loader


class Test(unittest.TestCase):
    def test_data_loader_tools(self):

        data = {
            "a": np.array([1, 2, 3]),
            "b": np.array([2, 3, 4]),
            "c": np.array([5, 6, 7]),
        }

        funcs = {
            "d": lambda df: df["a"] + df["b"],
            "e": lambda df: df.eval("b * c"),
            "f": lambda df: df.eval("d - e"),
        }

        # Test if we can load columns directly in the data
        load_df = make_data_loader(["a", "b", "c"])
        df = load_df(data)
        np.testing.assert_equal(df["a"], data["a"])
        np.testing.assert_equal(df["b"], data["b"])
        np.testing.assert_equal(df["c"], data["c"])

        # Test if we can get columns which are directly derived from the available columns
        load_df = make_data_loader(["a", "b", "c", "d", "e"], functions=funcs)
        df = load_df(data)
        np.testing.assert_equal(df["a"], data["a"])
        np.testing.assert_equal(df["b"], data["b"])
        np.testing.assert_equal(df["c"], data["c"])
        np.testing.assert_equal(df["d"], data["a"] + data["b"])
        np.testing.assert_equal(df["e"], data["b"] * data["c"])

        # Test if we can load columns which are "second-order derived" without loading anything else
        load_df = make_data_loader(["f"], functions=funcs)
        df = load_df(data)
        np.testing.assert_equal(df["f"], data["a"] + data["b"] - data["b"] * data["c"])


if __name__ == "__main__":

    unittest.main(verbosity=2)
