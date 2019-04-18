import os
import pickle
import pandas as pd
import h5py
import awkward
import numpy as np

from geeksw.utils import awkward_utils

vetoed_typenames = ["UprootIOWrapper", "TTree"]


def save(filename, item):

    typename = type(item).__name__

    if typename in vetoed_typenames:
        return False

    if typename == "DataFrame":
        item.to_hdf(filename, key="data")
        return True

    if typename in ["ndarray", "JaggedArray"]:
        with h5py.File(filename, "w") as hf:
            ah5 = awkward.hdf5(hf)
            if typename == "JaggedArray":
                ah5["data"] = awkward_utils.ascontiguousarray(item)
            else:
                ah5["data"] = np.ascontiguousarray(item)
        return True

    try:
        with open(filename, "wb") as f:
            pickle.dump(item, f)
        return True
    except:
        return False

    return False


def load(filename, typename):

    if typename == "DataFrame":
        return pd.read_hdf(filename, key="data")

    if typename in ["ndarray", "JaggedArray"]:
        with h5py.File(filename, "r") as hf:
            ah5 = awkward.hdf5(hf)
            array = ah5["data"]
        return array

    try:
        with open(filename, "rb") as pf:
            product = pickle.load(pf)
            return product
    except:
        return None

    return None


from lockfile import LockFile
import json
import os
import pickle


def pickle_save(filename, item):
    with open(filename, "wb") as f:
        pickle.dump(item, f)
    return True


def pickle_load(filename, typename):
    with open(filename, "rb") as f:
        out = pickle.load(f)
    return out


class IndexedCache(object):
    def __init__(self, path="~/.cache/geeksw", save=save, load=load):

        self._save = save
        self._load = load

        path = os.path.expanduser(path)

        if not os.path.exists(path):
            os.makedirs(path)

        self._path = path
        self._lock_filename = os.path.join(path, ".indexed-cache-lock")
        self._index_filename = os.path.join(path, "index.json")

    def _get_typename(self, key):
        type_name = None

        lock = LockFile(self._lock_filename)
        lock.acquire()

        try:
            with open(self._index_filename, "r") as f:
                index = json.load(f)
                if key in index:
                    type_name = index[key]
        except:
            pass

        lock.release()

        return type_name

    def __contains__(self, key):
        return not self._get_typename(key) is None

    def __setitem__(self, key, item):

        saved = False

        try:
            saved = self._save(os.path.join(self._path, key), item)
        except:
            saved = False

        if not saved:
            return

        lock = LockFile(self._lock_filename)
        lock.acquire()

        try:
            with open(self._index_filename, "r") as f:
                index = json.load(f)
        except:
            index = dict()

        index[key] = type(item).__name__

        with open(self._index_filename, "w") as f:
            json.dump(index, f, indent=4)

        lock.release()

    def __getitem__(self, key):
        type_name = self._get_typename(key)

        if type_name is None:
            raise ValueError("Key " + key + " not found in cache")

        out = self._load(os.path.join(self._path, key), type_name)
        return out
