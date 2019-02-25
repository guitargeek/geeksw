import os
import awkward
import uproot
import numpy as np
import h5py
from concurrent.futures import ThreadPoolExecutor


def list_files(dataset):
    cmd = 'dasgoclient -query="file dataset={0} system=phedex"'.format(dataset)
    file_list = os.popen(cmd).read()
    file_list = [f.strip() for f in file_list.split("\n") if ".root" in f]
    return file_list


def open_files(dataset, server):
    files = list_files(dataset)
    dataset = []
    for f in files:
        path = "root://"+server+"/"+f
        try:
            print("Opening a file directly")
            dataset.append(uproot.open(path))
        except:
            IOError("The file "+path+" could not be opened. Is it available on this site?")
    return dataset


class Dataset(object):

    def __init__(self, name, server, lazy=False, check=False):
        self._name = name
        self._server = server
        self._files = None
        self._check = check

        if not lazy:
            self._open_files()

    def _open_files(self):

        if self._check:
            cmd = 'dasgoclient -query="dataset={0}"'.format(self._name)
            dataset_list = os.popen(cmd).read().split("\n")[:-1]
            if len(dataset_list) > 1:
                raise ValueError("Dataset " + self._name + " not unique. Did you maybe use wildcards?")
            if len(dataset_list) < 1:
                raise ValueError("Dataset " + self._name + " does not seem to exist.")

        self._files = open_files(self._name, self._server)

    @property
    def files(self):
        if self._files is None:
            self._open_files()
        return self._files

    @property
    def name(self):
        return self._name


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
        with h5py.File(file_name, 'w') as hf:
            ah5 = awkward.hdf5(hf)
            ah5[key] = item

    def __contains__(self, key):
        file_name = self._get_file_name(key)
        return os.path.isfile(file_name)

    def __getitem__(self, key):
        print("Getting from cache...")
        file_name = self._get_file_name(key)

        if not key in self:
            raise KeyError(key +"not found in sratch cache.")

        with h5py.File(file_name) as hf:
            ah5 = awkward.hdf5(hf)
            array = ah5[key]

        return array


class UprootIOWrapper(object):

    def __init__(self, dataset=None, cache=None, verbose=False):
        self._verbose = verbose
        self._dataset = dataset
        self._working_dir = ""
        self._cache = cache # the persistent cache
        self._uproot_cache = uproot.cache.ThreadSafeArrayCache(limitbytes=1e9)

    def array(self, key):

        full_key = os.path.join(self._working_dir, key)
        cache_key = os.path.join(self._dataset.name, full_key)

        if cache_key in self._cache:
            return self._cache[cache_key]

        dirname = os.path.dirname(full_key)
        basename = os.path.basename(full_key)

        def load_array(i, f):
            if self._verbose:
                print("Reading array from file {0} of {1}...".format(i+1, len(self._dataset.files)))
            tree = f[dirname]
            return tree.array(basename, cache=self._uproot_cache)

        with ThreadPoolExecutor(max_workers=32) as executor:
            arrays = [executor.submit(load_array, i, f) for i, f in enumerate(self._dataset.files)]
        if len(arrays) == 1:
            array = arrays[0].result()
        elif isinstance(arrays[0], np.ndarray):
            array = np.concatenate([a.result() for a in arrays])
        else:
            array = arrays[0].result().concatenate([a.result() for a in arrays[1:]])

        if not self._cache is None:
            self._cache[cache_key] = array

        return array

    def __getitem__(self, key):
        out = UprootIOWrapper(dataset=self._dataset, cache=self._cache, verbose=self._verbose)
        out._working_dir = os.path.join(self._working_dir, key)
        return out

    def keys(self):
        if self._working_dir == "":
            return self._dataset.files[0].keys()
        keys = self._dataset.files[0][self._working_dir].keys()
        return [k.decode("utf-8") for k in keys]

    def allkeys(self):
        if self._working_dir == "":
            return self._dataset.files[0].keys()
        keys = self._dataset.files[0][self._working_dir].allkeys()
        return [k.decode("utf-8") for k in keys]


def load_dataset(name, cache=ScratchCache(), server="polgrid4.in2p3.fr"):

    # make sure there are no duplicate dashes
    l = len(name)
    l_new = -1
    while l_new != l:
        l = len(name)
        name = name.replace("//", "/")
        l_new = len(name)

    # make sure dataset name starts with a dash
    if not name.startswith("/"):
        name = "/" + name

    dataset = Dataset(name, server, lazy=True)

    return UprootIOWrapper(dataset=dataset, cache=cache)
