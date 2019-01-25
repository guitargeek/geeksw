import awkward
import numpy as np


class TableWrapper(awkward.Table):
    def __init__(self, *args, **kwargs):
        super(TableWrapper, self).__init__(*args, **kwargs)

        # The columns as attributes should only be used as read-only,
        # since setting via them doesn't run the validation!
        for col in self.columns:
            setattr(self, col, self._contents[col])

    @classmethod
    def fromtree(cls, tree, **branches):

        data = {}

        for key, col_name in branches.items():
            data[key] = tree.array(col_name)

        return cls(**data)

    def __getitem__(self, where):

        if isinstance(where, np.ndarray):
            if where.dtype == np.dtype("bool"):
                return self._slice_mask(where)

        if isinstance(where, awkward.JaggedArray):
            if where.content.dtype == bool:
                return self._slice_mask(where)

        return super(TableWrapper, self).__getitem__(where)

    def _slice_mask(self, mask):
        return TableWrapper([(key, x[mask]) for key, x in self._contents.items()])
