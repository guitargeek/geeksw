import os
import awkward
import uproot
import numpy as np
import h5py
from concurrent.futures import ThreadPoolExecutor


def list_files(dataset):
    cmd = 'dasgoclient -query="file dataset={0}"'.format(dataset)
    file_list = os.popen(cmd).read()
    file_list = [f.strip() for f in file_list.split("\n") if ".root" in f]
    return file_list


def open_files(dataset, server):
    files = list_files(dataset)
    dataset_opener = []
    for f in files:
        path = "root://"+server+"/"+f
        try:
            print("Opening a file directly")
            dataset_opener.append(uproot.open(path))
        except:
            IOError("The file "+path+" could not be opened. Is it available on this site?")
    return dataset_opener


class DatasetOpener(object):

    def __init__(self, dataset, server, lazy=False):
        self._dataset = dataset
        self._server = server
        self._files = None

        if not lazy:
            self._open_files()

    def _open_files(self):

        cmd = 'dasgoclient -query="dataset={0}"'.format(self._dataset)
        dataset_list = os.popen(cmd).read().split("\n")[:-1]
        if len(dataset_list) > 1:
            raise ValueError("Dataset " + self._dataset + " not unique. Did you maybe use wildcards?")
        if len(dataset_list) < 1:
            raise ValueError("Dataset " + self._dataset + " does not seem to exist.")

        self._files = open_files(list_files(dataset), server)

    @property
    def files(self):
        if self._files is None:
            self._open_files()
        return self._files


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

    def __init__(self, name, dataset_opener=None, cache=None, verbose=False):
        self._verbose = verbose
        self._name = name
        self._dataset_opener = dataset_opener
        self._working_dir = ""
        self._cache = cache # the persistent cache
        self._uproot_cache = uproot.cache.ThreadSafeArrayCache(limitbytes=1e9)

    @property
    def name(self):
        return self._name

    def array(self, key):

        full_key = os.path.join(self._working_dir, key)
        cache_key = os.path.join(self.name, full_key)

        if cache_key in self._cache:
            return self._cache[cache_key]

        dirname = os.path.dirname(full_key)
        basename = os.path.basename(full_key)

        def load_array(i, f):
            if self._verbose:
                print("Reading array from file {0} of {1}...".format(i+1, len(self._dataset_opener.files)))
            tree = f[dirname]
            return tree.array(basename, cache=self._uproot_cache)

        with ThreadPoolExecutor(max_workers=1) as executor:
            arrays = [executor.submit(load_array, i, f).result() for i, f in enumerate(self._dataset_opener.files)]
        if len(arrays) == 1:
            array = arrays[0]
        elif isinstance(arrays[0], np.ndarray):
            array = np.concatenate(arrays)
        else:
            array = arrays[0].concatenate(arrays[1:])

        if not self._cache is None:
            self._cache[cache_key] = array

        return array

    def __getitem__(self, key):
        out = UprootIOWrapper(self.name, cache=self._cache, verbose=self._verbose)
        out._dataset_opener = self._dataset_opener
        out._working_dir = os.path.join(self._working_dir, key)
        return out

    def keys(self):
        if self._working_dir == "":
            return self._dataset_opener.files[0].keys()
        keys = self._dataset_opener.files[0][self._working_dir].keys()
        return [k.decode("utf-8") for k in keys]

    def allkeys(self):
        if self._working_dir == "":
            return self._dataset_opener.files[0].keys()
        keys = self._dataset_opener.files[0][self._working_dir].allkeys()
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

    dataset_opener = DatasetOpener(name, server, lazy=True)

    return UprootIOWrapper(name, dataset_opener=dataset_opener, cache=cache)
