from geeksw.core import produces, requires

import numpy as np
import os.path


@produces("<dataset>/x")
def run(meta):

    path = os.path.join("datasets", meta.subs["<dataset>"], "data.npy")
    return np.load(path)
