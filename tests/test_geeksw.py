import unittest
from geeksw.core import geek_run
import os.path

class GeekswTests(unittest.TestCase):

    def test_geek_run(self):
        test_dir = os.path.dirname(__file__)

        # We give the config file as a string to keep the test more compact
        records = geek_run("""
producers = "producers"
products  = ["win/win",]
out_dir   = "test_geeksw_output"
""")

        for dataset, record in records.items():
            self.assertTrue(record._dict == dict())

if __name__ == '__main__':

    unittest.main(verbosity=2)
