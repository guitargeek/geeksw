import awkward
import numpy as np


class TableWrapper(awkward.Table):
    def __init__(self, *args, **kwargs):
        super(TableWrapper, self).__init__(*args, **kwargs)

        self._set_column_attributes()

    def _set_column_attributes(self):
        # The columns as attributes should only be used as read-only,
        # since setting via them doesn't run the validation!
        for col in self.columns:
            setattr(self, col, self._contents[col])

    @classmethod
    def fromtree(cls, tree, **branches):

        data = {}

        for key, col_name in branches.items():
            if isinstance(tree, list):
                data[key] = awkward.util.concatenate([t.array(col_name) for t in tree])
            else:
                data[key] = tree.array(col_name)

        return cls(**data)

    @classmethod
    def fromtable(cls, table):
        new = cls()
        new._view = table._view
        new._base = table._base
        new._rowname = table._rowname
        new._contents = table._contents
        return new

    def table(self):
        out = awkward.Table()
        out._view = self._view
        out._base = self._base
        out._rowname = self._rowname
        out._contents = self._contents
        return out

    def __getitem__(self, where):

        if isinstance(where, np.ndarray):
            if where.dtype == np.dtype("bool"):
                return self._slice_mask(where)

        if isinstance(where, awkward.JaggedArray):
            if where.content.dtype == bool:
                return self._slice_mask(where)

        return super(TableWrapper, self).__getitem__(where)

    def _slice_mask(self, mask):

        data = {}

        for key, x in self._contents.items():
            data[key] = x[mask]

        return type(self)(**data)
