import unittest
from geeksw.framework import geek_run
import os.path


class GeekswTests(unittest.TestCase):
    def test_geek_run(self):
        test_dir = os.path.dirname(__file__)

        # We give the config file as a string to keep the test more compact
        record = geek_run(
            """
datasets = [
            ("datasets/data1", "/data1"),
            ("datasets/data2", "/data2"),
            ("datasets/data3", "/data3"),
           ]
producers = "producers_1"
products  = ["/*/win/win"]
out_dir   = "test_output_1"
"""
        )

        self.assertTrue(record == dict())


if __name__ == "__main__":

    unittest.main(verbosity=2)
