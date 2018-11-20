import unittest
from geeksw.core import geek_run
import os.path

class GeekswPlotsTests(unittest.TestCase):

    def test_geek_run_plots(self):
        test_dir = os.path.dirname(__file__)
        record = geek_run("""
producers = "producers_with_plots"
products  = ["win/win","plot","other_plot"]
out_dir   = "test_geeksw_with_plots_output"
""")
        self.assertTrue(record._dict == dict())

if __name__ == '__main__':

    unittest.main(verbosity=2)
