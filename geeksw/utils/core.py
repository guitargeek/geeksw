import numpy as np


def concatenate(arrays):
    if len(arrays) == 1:
       return arrays[0]
    elif isinstance(arrays[0], np.ndarray):
        return np.concatenate([a for a in arrays])
    else:
        return arrays[0].concatenate([a for a in arrays[1:]])
