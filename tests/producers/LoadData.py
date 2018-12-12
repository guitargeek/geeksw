from geeksw.core import Producer

import numpy as np

class LoadData(Producer):

    product = "x"
    requires = []

    def run(self, inputs): 

        path = None

        return np.load(os.path.join(path, "data.npy"))
