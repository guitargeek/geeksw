import unittest
import geeksw.framework as geeksw


class GeekswTests(unittest.TestCase):
    def test_geek_run(self):

        datasets = ["/data1", "/data2", "/data3"]
        products  = ["/*/win/win"]

        record = geeksw.produce(products=products, producer_dir="producers", datasets=datasets)

        self.assertTrue("/data1/win/win" in record.keys())
        self.assertTrue("/data2/win/win" in record.keys())
        self.assertTrue("/data3/win/win" in record.keys())


if __name__ == "__main__":

    unittest.main(verbosity=2)
