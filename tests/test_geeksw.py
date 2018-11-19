import unittest
from geeksw.core import geek_run
import os.path

class GeekswTests(unittest.TestCase):

    def test_geek_run(self):
        test_dir = os.path.dirname(__file__)
        record = geek_run(os.path.join(test_dir, "producers"))
        self.assertTrue(record == dict())

if __name__ == '__main__':

    unittest.main(verbosity=2)
