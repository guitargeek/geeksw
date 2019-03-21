import unittest

import geeksw.framework as fwk


@fwk.one_producer("lin")
@fwk.consumes(foo="foo", jenkins="jenkins")
def a(foo, jenkins):

    return "Lin" + foo.title() + jenkins.title()


@fwk.one_producer("jenkins")
@fwk.consumes(foo="foo")
def b(foo):

    return foo + "Jenkins"


@fwk.one_producer("win/win")
@fwk.consumes(foo="foo", jenkins="jenkins")
def c(foo, jenkins):

    return "Win" + foo.title() + jenkins.title()


@fwk.one_producer("foo")
def d():

    return "foo"


producers = [a, b, c, d]


class Test(unittest.TestCase):
    def test_geek_run(self):

        datasets = ["/data1", "/data2", "/data3"]
        products = ["/*/win/win"]

        record = fwk.produce(products=products, producers=producers, datasets=datasets)

        self.assertTrue("/data1/win/win" in record.keys())
        self.assertTrue("/data2/win/win" in record.keys())
        self.assertTrue("/data3/win/win" in record.keys())


if __name__ == "__main__":

    unittest.main(verbosity=2)
