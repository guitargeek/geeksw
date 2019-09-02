import os
from collections import namedtuple
import pandas
import numpy


DatasetFileInfo = namedtuple("DatasetFileInfo", ["path", "root_basenames", "data_frames", "suffix"])


def expand_dataset_info(path):
    root_basenames = set()
    data_frames = set()
    for f in os.listdir(path):
        tmp = f.split("_")
        root_basenames.add(tmp[0])
        tmp = "_".join(tmp[1:]).split(".")
        data_frames.add(tmp[0])
        suffix = "." + ".".join(tmp[1:])

    return DatasetFileInfo(path, sorted(list(root_basenames)), sorted(list(data_frames)), suffix)


class ParquetSingleFileHandler(object):

    import pandas

    def __init__(self, file_template, data_frames):
        self._file_template = file_template
        self._data_frames = data_frames

    def keys(self):
        return self._data_frames[:]

    def __repr__(self):
        return "<ParquetSingleFileHandler for " + self._file_template + ">"

    def __contains__(self, key):
        return key in self._data_frames

    def __getitem__(self, key):
        if not key in self:
            raise ValueError("Dataset does not contain data frame named " + key + ".")
        df = pandas.read_parquet(self._file_template.format(key))
        return df.set_index("event")


class ParquetFilesHandler(object):
    def __init__(self, path):
        self._path, self._root_basenames, self._data_frames, self._suffix = expand_dataset_info(path)

    def __len__(self):
        return len(self._root_basenames)

    def keys(self):
        return self._data_frames[:]

    def __contains__(self, key):
        return key in self._data_frames

    def __getitem__(self, key):
        data_frame = None
        if hasattr(key, "__len__"):
            i, data_frame = key
        else:
            i = key
        file_template = os.path.join(self._path, self._root_basenames[i] + "_{}" + self._suffix)
        file_handler = ParquetSingleFileHandler(file_template, self._data_frames)
        if data_frame:
            return file_handler[data_frame]
        else:
            return file_handler

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]


def open(path):
    return ParquetFilesHandler(path)


def loc(df, selected_events, columns=None):
    e = df.index.values
    mask = numpy.in1d(e, selected_events)
    if columns is None:
        return df.loc[mask]
    else:
        return df.loc[mask, columns]
