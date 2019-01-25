class Dataset(object):
    def __init__(self, file_path, geeksw_path):
        self.file_path = file_path
        self.geeksw_path = geeksw_path


class Record(object):
    _dict = {}

    def __init__(self):
        pass

    def put(self, key, obj):
        self._dict[key] = obj

    def get(self, key):
        return self._dict[key]

    def to_list(self):
        return list(self._dict)

    def delete(self, key):
        del self._dict[key]


class FullRecord(object):
    _records = {}

    def __init__(self, datasets):
        for ds in datasets:
            self._records[ds.geeksw_path] = Record()

    def get(self, path):
        if type(path) == Dataset:
            return self._records[path.geeksw_path]
        if path == "**":
            records = {}
            for key, rcd in self._records.items():
                records[key] = rcd
            return records
        raise ValueError("Not implemented.")
