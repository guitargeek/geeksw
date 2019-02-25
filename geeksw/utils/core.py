import numpy as np
import pandas as pd


def concatenate(arrays):
    if len(arrays) == 1:
       return arrays[0]
    elif isinstance(arrays[0], np.ndarray):
        return np.concatenate(arrays)
    elif isinstance(arrays[0], pd.DataFrame):
        return pd.concat(arrays)
    else:
        return arrays[0].concatenate(arrays[1:])
