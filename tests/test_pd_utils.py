import unittest

import numpy as np
import pandas as pd

from geeksw.utils.pd_utils import format_errors_in_df

np.random.seed = 123


class Test(unittest.TestCase):
    def test_pd_utils(self):

        # check if format_errors_in_df works
        a = np.random.uniform(size=10)
        a_err = np.random.uniform(size=10) / np.random.uniform(0.0, 100.0, size=10)
        df = pd.DataFrame(dict(a=a, a_err=a_err))
        df_pretty = format_errors_in_df(df)


if __name__ == "__main__":

    unittest.main(verbosity=2)
