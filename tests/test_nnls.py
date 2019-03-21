import unittest
import numpy as np


class Test(unittest.TestCase):
    def test_nnls(self):
        import scipy.optimize.nnls
        from sklearn.datasets import make_regression
        import geeksw.optimize.nnls

        for i in range(20):
            A, b = make_regression(random_state=42, n_samples=100, n_features=15)

            x_geeksw = geeksw.optimize.nnls(A, b)
            x_scipy = scipy.optimize.nnls(A, b)[0]

            np.testing.assert_array_almost_equal(x_geeksw, x_scipy)


if __name__ == "__main__":

    unittest.main(verbosity=2)
