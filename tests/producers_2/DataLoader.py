from geeksw.core import Producer

import numpy as np

class DataLoader(Producer):

    product = "<dataset>/x"
    requires = []

    def run(self, inputs): 

        path = None

        # return np.load(os.path.join(path, "data.npy"))
        return self.product
