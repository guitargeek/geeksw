from geeksw.core import Producer

import numpy as np
import matplotlib.pyplot as plt

class Plotter(Producer):

    product = "plot"
    requires = ["*/x"]

    def run(self, inputs): 

        plt.figure()
        for k, v in inputs["*/x"].items():
           plt.hist(v, label=k)
        plt.legend(loc="upper right")
        plt.show()

        return None
