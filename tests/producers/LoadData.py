from geeksw.core import Plot
from geeksw.core import SingleDatasetProducer

import numpy as np

class LoadData(SingleDatasetProducer):

    produces = ["x"]

    def __init__(self):
        pass

    def run(self, dataset, record): 

        x = np.load(os.path.join(dataset.file_path, "data.npy"))
        record.put("x", x)
