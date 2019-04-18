import os
import uproot
from concurrent.futures import ThreadPoolExecutor


from ..utils.core import concatenate


def list_files(dataset_name):
    cmd = 'dasgoclient -query="file dataset={0} system=phedex"'.format(dataset_name)
    file_list = os.popen(cmd).read()
    file_list = [f.strip() for f in file_list.split("\n") if ".root" in f]
    file_list.sort()
    return sorted(file_list)


def open_files(dataset, server):
    files = list_files(dataset)
    opened_files = []
    for f in files:
        path = "root://" + server + "/" + f
        print("opening file " + f + "...")
        # try:
        opened_files.append(uproot.open(path))
        # except:
            # IOError("The file " + path + " could not be opened. Is it available on this site?")
    return opened_files


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

        # with ThreadPoolExecutor(max_workers=32) as executor:
            # arrays = [executor.submit(load_array, i, f) for i, f in enumerate(self.files)]
        arrays = [load_array(i, f) for i, f in enumerate(self.files)]
        array = concatenate(arrays)
        print("loaded arrays of length " + " + ".join([str(len(a)) for a in arrays]) + " = " + str((len(array))))

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
