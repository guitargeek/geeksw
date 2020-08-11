import numpy as np
import awkward


def awk_singleton(arr):
    return awkward.JaggedArray.fromcounts(np.ones(len(arr), dtype=np.int), arr)


def awksel(arr, selections, mask=None):
    if not mask is None:
        arr = arr[mask]
        for s in selections:
            arr = arr[awk_singleton(s[mask])].flatten()
    else:
        for s in selections:
            arr = arr[awk_singleton(s)].flatten()
    return arr


def repeat_value(value, n):
    """Creates an array [value, value, ..., value] with n entries.
    """
    return value + np.zeros(n, dtype=type(value))


def unpack_pair_values(df, column_getter, diagonal=None, jagged=False):
    """
    Example:
    
    You have a dataframe with invariant pair masses with the following columns:

    >>> [
    >>>     "VetoLeptonPair_mass_01",
    >>>     "VetoLeptonPair_mass_02",
    >>>     "VetoLeptonPair_mass_03",
    >>>     "VetoLeptonPair_mass_12",
    >>>     "VetoLeptonPair_mass_13",
    >>>     "VetoLeptonPair_mass_23",
    >>> ]
    
    Then you can "unpack" these symmetric pair values either into a numpy array or awkward array:
    
    >>> a = unpack_pair_values(samples["data"],
    >>>                        column_getter=lambda i, j : f"VetoLeptonPair_mass_{i}{j}",
    >>>                        diagonal=np.nan,
    >>>                        jagged=False)    
    """

    values = np.zeros((len(df), 4, 4))

    for i in range(4):
        values[:, i, i] = np.nan

    for i in range(4):
        for j in range(4):
            if not diagonal is None and i == j:
                values[:, i, j] = diagonal
                continue
            if i > j:
                continue
            values[:, i, j] = df[column_getter(i, j)]
            values[:, j, i] = values[:, i, j]

    if jagged:
        import awkward

        arr = awkward.JaggedArray.fromcounts(repeat_value(4, 4 * len(df)), values.flatten())
        arr_nested = awkward.JaggedArray.fromcounts(repeat_value(4, len(df)), arr)
        return arr_nested
    return values
