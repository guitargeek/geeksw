import unittest
from geeksw.core import geek_run
import os.path

class GeekswPlotsTests(unittest.TestCase):

    def test_geek_run_plots(self):
        test_dir = os.path.dirname(__file__)
        record = geek_run(os.path.join(test_dir, "producers_with_plots"))
        self.assertTrue(record._dict == dict())

if __name__ == '__main__':

    unittest.main(verbosity=2)
