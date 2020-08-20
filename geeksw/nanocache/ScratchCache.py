import os
import awkward
import h5py
import numpy as np


class ScratchCache(object):
    def __init__(self, cache_dir="/scratch/.nanocache/branches"):
        self._cache_dir = cache_dir

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_file_name(self, key):
        key = key.replace("/", "__")
        while key.startswith("_"):
            key = key[1:]
        return os.path.join(self._cache_dir, key + ".h5")

    def __setitem__(self, key, item):
        file_name = self._get_file_name(key)
        with h5py.File(file_name, "w") as hf:
            ah5 = awkward.hdf5(hf)
            ah5[key] = item

    def __contains__(self, key):
        file_name = self._get_file_name(key)
        return os.path.isfile(file_name)

    def __getitem__(self, key):
        print("Getting from cache {0}...".format(key))
        file_name = self._get_file_name(key)

        if not key in self:
            raise KeyError(key + "not found in scratch cache.")

        with h5py.File(file_name, "r") as hf:
            ah5 = awkward.hdf5(hf)
            array = ah5[key]

        if isinstance(array, np.ndarray):
            print("got ndarray of length " + str(len(array)))
        else:
            print("got jagged array of length " + str(len(array)) + " (flattened " + str(len(array.flatten())) + ")")
        return array
