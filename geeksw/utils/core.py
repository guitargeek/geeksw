import numpy as np
import pandas as pd
from geeksw.data_formats import Cutflow


def concatenate(arrays):
    if len(arrays) == 1:
        return arrays[0]
    elif isinstance(arrays[0], np.ndarray):
        return np.concatenate(arrays)
    elif isinstance(arrays[0], pd.DataFrame):
        df = pd.concat(arrays)
        df.index = np.arange(len(df))
        return df
    elif isinstance(arrays[0], Cutflow):
        return Cutflow.average(arrays)
    else:
        return arrays[0].concatenate(arrays[1:])
