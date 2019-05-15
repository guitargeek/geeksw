import numpy as np
import awkward


def ascontiguousarray(array):
    counts = array.counts
    offsets = array.counts2offsets(counts)
    starts = offsets[:-1]
    stops = offsets[1:]
    return awkward.JaggedArray(starts, stops, array.flatten())


def selection2mask(selection, array):
    """Convert at jagged array of index type into a jagged array of boolean
    types to mask an other array.

    Args:
        selection (awkward.array.jagged.JaggedArray of index type):
            A jagged array with indices that can be used to select from the
            other array given as the second argument.
        array (awkward.array.jagged.JaggedArray):
            The array that the selection applies to.

    Returns:
        awkward.array.jagged.JaggedArray of dtype bool:
            A mask that selects the same elements from the array as the
            original selection.
    """
    counts = array.counts
    mask = np.zeros(len(array.flatten()), dtype=array.MASKTYPE)
    selected_indices = ((np.cumsum(counts) - counts) + selection).flatten()
    mask[selected_indices] = True
    offsets = array.counts2offsets(counts)
    starts = offsets[:-1]
    stops = offsets[1:]
    return awkward.JaggedArray(starts, stops, mask)


def jagged_single_flatten_fillna(array, value):
    if np.max(array.counts) > 1:
        raise ValueError("There should not be no more than one element per jagged entry!")
    out = np.zeros(len(array)) + value
    out[array.counts > 0] = array.flatten()

    return out
