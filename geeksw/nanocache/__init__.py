import os
import awkward
import uproot
import numpy as np
import h5py
from concurrent.futures import ThreadPoolExecutor

def concatenate(arrays):
    if len(arrays) == 1:
       return arrays[0]
    elif isinstance(arrays[0], np.ndarray):
        return np.concatenate([a for a in arrays])
    else:
        return arrays[0].concatenate([a for a in arrays[1:]])

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

    def array(self, key, cache=None):

        cache_key = os.path.join(self._name, key)

        if not cache is None:
            if cache_key in cache:
                return cache[cache_key]

        dirname = os.path.dirname(key)
        basename = os.path.basename(key)

        def load_array(i, f):
            tree = f[dirname]
            return tree.array(basename)

        with ThreadPoolExecutor(max_workers=32) as executor:
            arrays = [executor.submit(load_array, i, f) for i, f in enumerate(self.files)]
        array = concatenate([a.result() for a in arrays])

        if not cache is None:
            cache[cache_key] = array

        return array

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
        print("Getting from cache {0}...".format(key))
        file_name = self._get_file_name(key)

        if not key in self:
            raise KeyError(key +"not found in scratch cache.")

        with h5py.File(file_name) as hf:
            ah5 = awkward.hdf5(hf)
            array = ah5[key]

        return array


class UprootIOWrapper(object):

    def __init__(self, datasets=None, cache=None, verbose=False):
        self._verbose = verbose
        self._datasets = datasets
        self._working_dir = ""
        self._cache = cache # the persistent cache
        self._uproot_cache = uproot.cache.ThreadSafeArrayCache(limitbytes=1e9)

    def array(self, key):
        full_key = os.path.join(self._working_dir, key)
        arrays = [dset.array(full_key, self._cache) for dset in self._datasets]
        return concatenate(arrays)

    def __getitem__(self, key):
        out = UprootIOWrapper(datasets=self._datasets, cache=self._cache, verbose=self._verbose)
        out._working_dir = os.path.join(self._working_dir, key)
        return out

    def keys(self):
        if self._working_dir == "":
            return self._datasets[0].files[0].keys()
        keys = self._datasets[0].files[0][self._working_dir].keys()
        return [k.decode("utf-8") for k in keys]

    def allkeys(self):
        if self._working_dir == "":
            return self._datasets[0].files[0].keys()
        keys = self._datasets[0].files[0][self._working_dir].allkeys()
        return [k.decode("utf-8") for k in keys]

def trim_name(name):
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
    
    return name


def load_datasets(names, cache=ScratchCache(), server="polgrid4.in2p3.fr"):

    names = [trim_name(n) for n in names]

    if type(names) == str:
        names = [names]
    if type(names) == list:
        datasets = [Dataset(n, server, lazy=True) for n in names]
    else:
        raise TypeError("Argument names has to be string or list")

    return UprootIOWrapper(datasets=datasets, cache=cache)

def load_dataset(name, cache=ScratchCache(), server="polgrid4.in2p3.fr"):
    return load_datasets([name], cache=cache, server=server)
