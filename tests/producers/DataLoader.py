from geeksw.framework import produces, consumes

import numpy as np
import os.path


@produces("<dataset>/x")
def run(meta):

    path = os.path.join("datasets/random_numbers", meta.subs["<dataset>"], "data.npy")
    return np.load(path)
