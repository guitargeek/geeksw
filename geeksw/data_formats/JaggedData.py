import awkward


class JaggedData(object):

    _columns = []
    _data = []

    def __init__(self, **data):

        for col_name, arr in data.items():
            if not isinstance(arr, awkward.JaggedArray):
                class_name = self.__class__.__name__
                raise TypeError(
                    "Items of " + class_name + "have to be of class JaggedArray!"
                )
            self._data.append(arr)
            self._columns.append(col_name)

            # The columns as attributes should only be used as read-only,
            # since setting via them doesn't run the validation!
            setattr(self, col_name, arr)

        self._validate()

    @classmethod
    def fromtree(cls, tree, **branches):

        data = {}

        for key, col_name in branches.items():
            data[key] = tree.array(col_name)

        return cls(**data)

    def _validate(self):
        if self._data == []:
            return

        for col, arr in zip(self._columns, self._data):
            if not (self._data[0].offsets == arr.offsets).all():
                raise ValueError(
                    "Column "
                    + col
                    + " is not of same shape as "
                    + self._columns[0]
                    + "!"
                )

    def __getitem__(self, key):
        return self._data[self._columns.index(key)]

    def __setitem__(self, key, item):
        if not isinstance(item, awkward.JaggedArray):
            class_name = self.__class__.__name__
            raise TypeError(
                "Items of " + class_name + "have to be of class JaggedArray!"
            )
        self._columns.append(key)
        self._data.append(item)
        self._validate()

    def __delitem__(self, key):
        index = self._columns.index(key)
        self._columns.pop(index)
        self._data.pop(index)

    @property
    def columns(self):
        return self._columns

    def __len__(self):
        return len(self._data[0])

    def __repr__(self):
        class_name = self.__class__.__name__
        content_size = len(self._data[0].content)
        return class_name + f" of length {len(self)} and content length {content_size}"
