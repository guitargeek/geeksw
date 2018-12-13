from geeksw.core import Producer

import numpy as np

class Plotter(Producer):

    product = "plot"
    requires = ["*/x"]

    def run(self, inputs): 

        return None
