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
