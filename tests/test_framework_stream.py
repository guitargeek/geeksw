import unittest
import geeksw.framework as fwk
import uproot
import awkward

# Declare producers for this test


@fwk.one_producer("trees", stream=True)
def load_tree():

    trees = [uproot.open("tests/datasets/WWZ/nano_{0}.root".format(i))["Events"] for i in range(4)]

    print("Total number of events:")
    print(sum([len(t) for t in trees]))

    return trees


@fwk.stream_producer("data")
@fwk.consumes(trees="trees")
def load_branch(trees):

    data = trees.array("Electron_pt")
    print("Calculator got data of length {0}".format(len(data)))

    return data


@fwk.one_producer("merged")
@fwk.consumes(data="data")
def merge_branch(data):

    return data


producers = [load_tree, load_branch, merge_branch]


class Test(unittest.TestCase):
    def test_geek_run(self):

        datasets = ["/WWZ"]
        products = ["/WWZ/merged"]

        record = fwk.produce(products=products, producers=producers, datasets=datasets, max_workers=32)

        print("Length of final record:")
        print(len(record["WWZ/merged"]))

        self.assertTrue("WWZ/merged" in record.keys())


if __name__ == "__main__":

    unittest.main(verbosity=2)
