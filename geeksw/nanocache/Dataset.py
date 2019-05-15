import os
import uproot
from tqdm import trange


from ..utils.core import concatenate


def list_files(dataset_name):
    cmd = 'dasgoclient -query="file dataset={0} system=phedex"'.format(dataset_name)
    file_list = os.popen(cmd).read()
    file_list = [f.strip() for f in file_list.split("\n") if ".root" in f]
    file_list.sort()
    return sorted(file_list)


class Dataset(object):
    def __init__(self, name, server, check=False):
        self._name = name
        self._server = server
        self._files = None
        self._check = check

        if self._check:
            cmd = 'dasgoclient -query="dataset={0}"'.format(self._name)
            dataset_list = os.popen(cmd).read().split("\n")[:-1]
            if len(dataset_list) > 1:
                raise ValueError("Dataset " + self._name + " not unique. Did you maybe use wildcards?")
            if len(dataset_list) < 1:
                raise ValueError("Dataset " + self._name + " does not seem to exist.")

        files = list_files(self._name)
        filenames = []
        for f in files:
            path = self._server + "/" + f
            filenames.append(path)

        self._filenames = filenames

    def array(self, key, cache=None):

        cache_key = os.path.join(self._name, key)

        if not cache is None:
            if cache_key in cache:
                return cache[cache_key]

        dirname = os.path.dirname(key)
        basename = os.path.basename(key)

        arrays = []
        print("Loading " + key + " from dataset " + self._name)
        t = trange(len(self._filenames), ascii=True)
        for i in t:
            tree = uproot.open(self._filenames[i])[dirname]
            arrays.append(tree.array(basename))
        array = concatenate(arrays)

        if not cache is None:
            cache[cache_key] = array

        return array

    @property
    def name(self):
        return self._name
