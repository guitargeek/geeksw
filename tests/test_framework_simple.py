import unittest
import geeksw.framework as geeksw
from geeksw.framework import produces, consumes

# Declare producers for this test

@produces("lin")
@consumes(foo="foo", jenkins="jenkins")
def a(foo, jenkins):

    return "Lin" + foo.title() + jenkins.title()


@produces("jenkins")
@consumes(foo="foo")
def b(foo):

    return foo + "Jenkins"


@produces("win/win")
@consumes(foo="foo", jenkins="jenkins")
def c(foo, jenkins):

    return "Win" + foo.title() + jenkins.title()


@produces("foo")
def d():

    return "foo"


producers = [a, b, c, d]


class GeekswTests(unittest.TestCase):

    def test_geek_run(self):

        datasets = ["/data1", "/data2", "/data3"]
        products  = ["/*/win/win"]

        record = geeksw.produce(products=products, producers=producers, datasets=datasets)

        self.assertTrue("/data1/win/win" in record.keys())
        self.assertTrue("/data2/win/win" in record.keys())
        self.assertTrue("/data3/win/win" in record.keys())


if __name__ == "__main__":

    unittest.main(verbosity=2)
