from geeksw.core import Producer

import numpy as np
import os.path

class DataLoader(Producer):

    product = "<dataset>/x"
    requires = []

    def run(self, inputs): 

        path = os.path.join("datasets", self.subs["<dataset>"], "data.npy")
        return np.load(path)
