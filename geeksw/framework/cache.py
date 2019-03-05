import glob
import os
import pickle
import pandas as pd
import h5py
import awkward

from .utils import mkdir


class FrameworkCache(object):
    def __init__(self, cache_dir):

        # Create the cache dir structure
        mkdir(cache_dir)

        self.cache_dir = cache_dir

    def __setitem__(self, key, item):

        name = key
        key = key.replace("/", "_")

        classname = type(item).__name__
        filename = os.path.join(self.cache_dir, key + "__" + classname)

        if classname == "DataFrame":
            item.to_hdf(filename + ".h5", key="data")

        if classname in ["ndarray", "JaggedArray"]:
            with h5py.File(filename + ".h5", "w") as hf:
                ah5 = awkward.hdf5(hf)
                ah5["data"] = item

        try:
            with open(filename + ".pkl", "wb") as f:
                pickle.dump(item, f)
        except pickle.PicklingError as e:
            print("Product " + name + " could not be cached.")

    def __getitem__(self, key):

        filename = self._get_file(key)

        key = key.replace("/", "_")

        if filename is None:
            raise ValueError("Product " + key + " not found in cache!")

        if "__DataFrame" in filename:
            return pd.read_hdf(filename, key="data")

        if "__ndarray" in filename or "__JaggedArray" in filename:
            with h5py.File(filename) as hf:
                ah5 = awkward.hdf5(hf)
                array = ah5["data"]
            return array

        if os.path.isfile(filename + ".pkl"):
            with open(filename + ".pkl", "rb") as pf:
                product = pickle.load(pf)
            return product

    def _get_file(self, key):
        cache_file_wo_suffix = os.path.join(self.cache_dir, key.replace("/", "_"))
        res = glob.glob(cache_file_wo_suffix + "*")
        if res:
            return res[0]
        if len(res) > 0:
            pass
        return None

    def __contains__(self, key):
        if self._get_file(key):
            return True
        return False
