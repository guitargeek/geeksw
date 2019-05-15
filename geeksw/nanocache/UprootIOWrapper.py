import os
import uproot


from ..utils.core import concatenate


class UprootIOWrapper(object):
    def __init__(self, datasets=None, cache=None, verbose=False):
        self._verbose = verbose
        self._datasets = datasets
        self._working_dir = ""
        self._cache = cache  # the persistent cache

    def array(self, key):
        full_key = os.path.join(self._working_dir, key)
        arrays = [dset.array(full_key, self._cache) for dset in self._datasets]
        return concatenate(arrays)

    def __getitem__(self, key):
        out = UprootIOWrapper(datasets=self._datasets, cache=self._cache, verbose=self._verbose)
        out._working_dir = os.path.join(self._working_dir, key)
        return out

    def keys(self):
        opened_file = uproot.open(self._datasets[0].files[0])
        if self._working_dir == "":
            return opened_file.keys()
        keys = opened_file[self._working_dir].keys()
        return [k.decode("utf-8") for k in keys]

    def allkeys(self):
        opened_file = uproot.open(self._datasets[0].files[0])
        if self._working_dir == "":
            return opened_file.allkeys()
        keys = opened_file[self._working_dir].allkeys()
        return [k.decode("utf-8") for k in keys]
