import unittest
import geeksw.framework as geeksw
import os.path


class GeekswTests(unittest.TestCase):
    def test_geek_run(self):
        test_dir = os.path.dirname(__file__)


        datasets = [
                    ("datasets/random_numbers/data1", "/data1"),
                    ("datasets/random_numbers/data2", "/data2"),
                    ("datasets/random_numbers/data3", "/data3"),
                   ]
        products  = ["/*/win/win"]

        record = geeksw.produce(products=products, producer_dir="producers_1", datasets=datasets)


        self.assertTrue("/data1/win/win" in record.keys())
        self.assertTrue("/data2/win/win" in record.keys())
        self.assertTrue("/data3/win/win" in record.keys())


if __name__ == "__main__":

    unittest.main(verbosity=2)
