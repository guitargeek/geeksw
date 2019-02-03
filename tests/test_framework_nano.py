import unittest
import geeksw.framework as fwk
import uproot
import awkward
import time

# Declare producers for this test

@fwk.global_to_stream
@fwk.produces("trees")
def load_tree():

    trees = [uproot.open(f"./datasets/WWZ/nano_{i}.root")["Events"] for i in range(4)]

    print("Total number of events:")
    print(sum([len(t) for t in trees]))

    return trees


@fwk.stream_to_stream
@fwk.produces("data")
@fwk.consumes(trees="trees")
def load_branch(trees):

    time.sleep(3)

    data = trees.array("Electron_pt")
    print("Calculator got data of length {0}".format(len(data)))

    return data


@fwk.stream_to_global(awkward.JaggedArray.concatenate)
@fwk.produces("merged")
@fwk.consumes(data="data")
def merge_branch(data):

    return data


producers = [
        load_tree,
        load_branch,
        merge_branch,
        ]


class GeekswTests(unittest.TestCase):

    def test_geek_run(self):

        datasets = ["/WWZ"]
        products  = ["/WWZ/merged"]

        record = fwk.produce(products=products, producers=producers, datasets=datasets, max_workers=32)

        print("Length of final record:")
        print(len(record["WWZ/merged"]))

        self.assertTrue("WWZ/merged" in record.keys())


if __name__ == "__main__":

    unittest.main(verbosity=2)
