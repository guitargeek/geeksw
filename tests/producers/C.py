from geeksw.core import Plot
import matplotlib.pyplot as plt
import numpy as np

class C:

    outputs  = ["win", "plot", "other_plot"]
    requires = ["foo", "jenkins"]

    def __init__(self):
        pass

    def run(self, record): 

        record["win"] = "Win"+record["foo"].title()+record["jenkins"].title()

        x = np.linspace(0, 5, 200)
        y = np.sin(x)

        record["plot"] = Plot()
        plt.plot(x, y)
        plt.xlabel("x")
        plt.ylabel("y")
        record["plot"].commit()

        record["other_plot"] = Plot()
        plt.plot(y, x)
        plt.xlabel("y")
        plt.ylabel("x")
        record["other_plot"].commit()
