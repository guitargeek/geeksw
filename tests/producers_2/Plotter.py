from geeksw.core import produces, requires

import numpy as np
import matplotlib.pyplot as plt


@produces("plot")
@requires(x="*/x")
def run(x):

    plt.figure()
    for k, v in x:
        plt.hist(v, label=k)
    plt.legend(loc="upper right")
    plt.show()

    return None
