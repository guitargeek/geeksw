import unittest
import geeksw.framework as fwk
import uproot
import awkward
import pandas as pd
import numpy as np

import time

@fwk.one_producer("data_token")
def open_data():
    """ Simulate some time consuming data producer that depends on some other product.
    """
    return True


@fwk.one_producer("data")
@fwk.consumes(token="data_token")
def read_data(token):
    """ Simulate some time consuming data producer that depends on some other product.
    """
    time.sleep(1)
    df = pd.DataFrame(np.random.randint(0,100,size=(100, 4)), columns=list('ABCD'))
    return df


producers = [open_data, read_data]


class Test(unittest.TestCase):
    def test_framework_cache(self):

        record = fwk.produce(products=["/data"], producers=producers, max_workers=32, cache_time=0.1)

        # print(record)
        # print("Length of final record:")
        # print(len(record["WWZ/merged"]))

        # self.assertTrue("WWZ/merged" in record.keys())


if __name__ == "__main__":

    unittest.main(verbosity=2)
