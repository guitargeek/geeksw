import numpy as np
import matplotlib.pyplot as plt


def plothist(hist, bin_edges, baseline=None, histtype="bar", **kwargs):
    """Plot a histogram from the hist and bin edges as returned by numpy.histogram.
    """
    if not histtype == "bar":
        raise NotImplementedError
    zero = np.zeros(1, dtype=hist.dtype)
    x = np.concatenate([bin_edges, [bin_edges[-1]]])
    if baseline is None:
        y = np.concatenate([zero, hist, zero])
        plt.step(x, y, where="pre", **kwargs)
    else:
        y1 = np.concatenate([zero, baseline, zero])
        y2 = np.concatenate([zero, baseline + hist, zero])
        plt.fill_between(x, y1, y2, step="pre", **kwargs)
