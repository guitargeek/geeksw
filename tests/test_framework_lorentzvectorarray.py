import unittest
import uproot
import awkward
import uproot_methods
import numpy as np
import shutil
import geeksw.framework as fwk
from geeksw.data_formats import Cutflow


cache_dir = ".test_framework_cache"


@fwk.one_producer("trees", stream=True)
def load_tree():
    return [uproot.open("tests/datasets/WWZ/nano_{0}.root".format(i))["Events"] for i in range(4)]


@fwk.stream_producer("electrons")
@fwk.consumes(trees="trees")
def load_branch(trees):

    pt = trees.array("Electron_pt")
    eta = trees.array("Electron_eta")
    phi = trees.array("Electron_phi")
    mass = trees.array("Electron_mass")

    electrons = uproot_methods.TLorentzVectorArray.from_ptetaphim(pt, eta, phi, mass)
    electrons["charge"] = trees.array("Electron_charge")

    return electrons


class Test(unittest.TestCase):
    def test_framework_lorentzvectorarray(self):

        datasets = ["/WWZ"]
        products = ["/WWZ/electrons"]

        producers = [load_branch, load_tree]

        record = fwk.produce(
            products=products,
            producers=producers,
            datasets=datasets,
            max_workers=32,
            cache_time=0.0,
            cache_dir=cache_dir,
        )

        producers = [load_branch]

        record_cached = fwk.produce(
            products=products,
            producers=producers,
            datasets=datasets,
            max_workers=32,
            cache_time=0.0,
            cache_dir=cache_dir,
        )

        shutil.rmtree(cache_dir)

        np.testing.assert_array_almost_equal(
            record["WWZ/electrons"][0].pt.flatten(), record_cached["WWZ/electrons"][0].pt.flatten()
        )
        np.testing.assert_array_almost_equal(
            record["WWZ/electrons"][0]["charge"].flatten(), record_cached["WWZ/electrons"][0]["charge"].flatten()
        )


if __name__ == "__main__":

    unittest.main(verbosity=2)
