import unittest
import geeksw.framework as fwk
import uproot
import awkward

# Declare producers for this test

@fwk.global_to_stream
@fwk.produces("data")
def DataLoader():

    trees = [uproot.open(f"./datasets/WWZ/nano_{i}.root")["Events"] for i in range(4)]

    print("Total number of events:")
    print(sum([len(t) for t in trees]))

    return [t.array("Electron_pt") for t in trees]


@fwk.stream_to_stream
@fwk.produces("calculation")
@fwk.consumes(data="data")
def Calculator(data):

    print("Calculator got data of length {0}".format(len(data)))
    return data


@fwk.stream_to_global(awkward.JaggedArray.concatenate)
@fwk.produces("merged")
@fwk.consumes(calculation="calculation")
def Merger(calculation):

    return calculation


producers = [
        DataLoader,
        Calculator,
        Merger,
        ]


class GeekswTests(unittest.TestCase):

    def test_geek_run(self):

        datasets = ["/WWZ"]
        products  = ["/WWZ/merged"]

        record = fwk.produce(products=products, producers=producers, datasets=datasets)

        print("Length of final record:")
        print(len(record["WWZ/merged"]))

        self.assertTrue("WWZ/merged" in record.keys())


if __name__ == "__main__":

    unittest.main(verbosity=2)
