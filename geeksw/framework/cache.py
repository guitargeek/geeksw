import glob
import os
import pickle

from .utils import mkdir


class FrameworkCache(object):

    def __init__(self, cache_dir):

        # Create the cache dir structure
        mkdir(cache_dir)

        self.cache_dir = cache_dir

    def __setitem__(self, key, item):

        key = key.replace("/", "__")

        try:
            file_name = os.path.join(self.cache_dir, key + ".pkl")
            with open(file_name, "wb") as f:
                pickle.dump(item, f)
        except pickle.PicklingError as e:
            print("Product " + name + " could not be pickled.")

    def __getitem__(self, key):

        if not key in self:
            raise ValueError("Product " + key + " not found in cache!")

        filename = key.replace("/", "__")

        cache_file_name = os.path.join(self.cache_dir, filename + ".pkl")
        if os.path.isfile(cache_file_name):
            return pickle.load(open(cache_file_name, "rb"))

    def __contains__(self, key):
        cache_file_wo_suffix = os.path.join(self.cache_dir, key.replace("/", "__"))
        if glob.glob(cache_file_wo_suffix + "*"):
            return True
        return False
