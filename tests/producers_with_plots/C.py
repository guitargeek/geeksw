import matplotlib.pyplot as plt
import numpy as np

from geeksw.core import Plot

class C:

    produces = ["win", "plot", "other_plot"]
    requires = ["foo", "jenkins"]

    def __init__(self):
        pass

    def run(self, record): 

        record.put("win", "Win"+record.get("foo").title()+record.get("jenkins").title())

        x = np.linspace(0, 5, 200)
        y = np.sin(x)

        plot = Plot()
        plt.plot(x, y)
        plt.xlabel("x")
        plt.ylabel("y")
        plot.commit()
        record.put("plot", plot)

        plot = Plot()
        plt.plot(y, x)
        plt.xlabel("y")
        plt.ylabel("x")
        plot.commit()
        record.put("other_plot", plot)
