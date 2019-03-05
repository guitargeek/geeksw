import unittest
import numpy as np
import torch
import geeksw.nptorch as nt


class Test(unittest.TestCase):
    def test_nptorch(self):

        a = np.random.uniform(size=10)
        t = torch.tensor(a)

        def test_f(f, f_ref):
            np.testing.assert_array_almost_equal(f(a), f(t).numpy())
            np.testing.assert_array_almost_equal(f_ref(a), f(a))

        test_f(nt.exp, np.exp)
        test_f(nt.cos, np.cos)
        test_f(nt.sin, np.sin)
        test_f(nt.tan, np.tan)
        test_f(nt.sqrt, np.sqrt)


if __name__ == "__main__":

    unittest.main(verbosity=2)
