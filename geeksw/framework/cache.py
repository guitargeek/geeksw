import glob
import os
import pickle
import pandas as pd
import h5py
import awkward
from collections import OrderedDict
import uproot_methods
import numpy as np
import torch

from .utils import mkdir
from .stream import StreamList
from geeksw.utils import awkward_utils

vetoed_classnames = ["UprootIOWrapper", "TTree"]


def _save_to_cache(filename, item):

    classname = type(item).__name__

    if classname in vetoed_classnames:
        return

    if classname == "StreamList":
        if type(item[0]).__name__ in vetoed_classnames:
            return
        mkdir(filename)
        for i, subitem in enumerate(item):
            subclassname = type(subitem).__name__
            if subclassname == "StreamList":
                raise TypeError("StreamList in a StreamList found, which should not happen.")
            subfilename = os.path.join(
                filename, os.path.basename(filename.replace(classname, subclassname)) + "__{0:04d}".format(i)
            )
            _save_to_cache(subfilename, subitem)
        return

    if classname == "DataFrame":
        item.to_hdf(filename + ".h5", key="data")
        return

    if classname in ["ndarray", "JaggedArray"]:
        with h5py.File(filename + ".h5", "w") as hf:
            ah5 = awkward.hdf5(hf)
            if classname == "JaggedArray":
                ah5["data"] = awkward_utils.ascontiguousarray(item)
            else:
                ah5["data"] = np.ascontiguousarray(item)
        return

    # For TLorentsVectorArray from ptetaphimass
    if (
        classname == "JaggedArrayMethods"
        and type(item._content).__name__ == "PtEtaPhiMassLorentzVectorArray"
        and type(item._content._content).__name__ == "Table"
    ):
        starts = item._starts
        stops = item._stops
        contents = item._content._content._contents
        filename = filename.replace("JaggedArrayMethods", "JaggedArrayMethods_PtEtaPhiMassLorentzVectorArray_Table")
        with h5py.File(filename + ".h5", "w") as hf:
            ah5 = awkward.hdf5(hf)
            for k, v in contents.items():
                a = awkward.JaggedArray(starts, stops, v)
                ah5[k] = awkward_utils.ascontiguousarray(a)
        return

    # for pytorch nn models
    if issubclass(type(item), torch.nn.Module):
        torch.save(item, filename + ".pt")
        return

    with open(filename + ".pkl", "wb") as f:
        pickle.dump(item, f)
    return


def _get_from_cache(filename):

    basename = os.path.basename(filename)

    if "__StreamList" in basename:
        filenames = glob.glob(filename + "/*")
        stream_list = StreamList([_get_from_cache(f) for f in sorted(filenames)])
        return stream_list

    if "__DataFrame" in basename:
        return pd.read_hdf(filename, key="data")

    # For TLorentsVectorArray from ptetaphimass
    if "JaggedArrayMethods_PtEtaPhiMassLorentzVectorArray_Table" in basename:
        content = OrderedDict()
        with h5py.File(filename, "r") as hf:
            ah5 = awkward.hdf5(hf)
            for k in ah5:
                content[k] = ah5[k]
        particles = uproot_methods.TLorentzVectorArray.from_ptetaphim(
            content["fPt"], content["fEta"], content["fPhi"], content["fMass"]
        )
        for k in content:
            if k not in ["fPt", "fEta", "fPhi", "fMass"]:
                particles[k] = content[k]
        return particles

    if "__ndarray" in basename or "__JaggedArray" in basename:
        with h5py.File(filename, "r") as hf:
            ah5 = awkward.hdf5(hf)
            array = ah5["data"]
        return array

    # for pytorch nn models
    if filename.endswith(".pt"):
        model = torch.load(filename)
        model.eval()
        return model

    if filename.endswith(".pkl"):
        with open(filename, "rb") as pf:
            product = pickle.load(pf)
        return product


class FrameworkCache(object):
    def __init__(self, cache_dir):

        # Create the cache dir structure
        mkdir(cache_dir)

        self.cache_dir = cache_dir

    def __setitem__(self, key, item):

        name = key
        key = key.replace("/", "_")

        filename = os.path.join(self.cache_dir, key + "__" + type(item).__name__)

        try:
            _save_to_cache(filename, item)
        except:
            print("Product " + name + " could not be cached.")

    def __getitem__(self, key):

        filename = self._get_file(key)

        key = key.replace("/", "_")

        if filename is None:
            raise ValueError("Product " + key + " not found in cache!")

        return _get_from_cache(filename)

    def _get_file(self, key):
        cache_file_wo_suffix = os.path.join(self.cache_dir, key.replace("/", "_")) + "__"
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
