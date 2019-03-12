import unittest
import numpy as np
import matplotlib.pyplot as plt
from geeksw.data_formats import Cutflow


class Test(unittest.TestCase):
    def test_cutflow(self):

        np.random.seed(41)

        x0 = np.random.uniform(size=(2, 1000))
        x1 = np.random.uniform(size=(2, 10000))

        x = np.concatenate([x0.T, x1.T]).T
        nbegin = len(x[0])
        nend = np.sum(np.logical_and.reduce([x[0] > 0.1, x[0] < 0.9, x[1] > 0.1, x[1] < 0.9]))

        final_efficiency = float(nend) / nbegin

        cutflow00 = Cutflow.frommasks([x0[0] > 0.1, x0[1] > 0.1], ["cut0", "cut1"])
        x0 = cutflow00(x0.T).T

        cutflow01 = Cutflow.frommasks([x0[0] < 0.9, x0[1] < 0.9], ["cut2", "cut3"])

        cutflow10 = Cutflow.frommasks([x1[0] > 0.1, x1[1] > 0.1], ["cut0", "cut1"])
        x1 = cutflow10(x1.T).T

        cutflow11 = Cutflow.frommasks([x1[0] < 0.9, x1[1] < 0.9], ["cut2", "cut3"])

        cutflow0 = cutflow00 * cutflow01
        cutflow1 = cutflow10 * cutflow11

        cutflow = Cutflow.average([cutflow0, cutflow1])

        self.assertAlmostEquals(cutflow.efficiencies[-1], final_efficiency)


if __name__ == "__main__":

    unittest.main(verbosity=2)
