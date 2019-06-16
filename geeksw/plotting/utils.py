import numpy as np
import matplotlib.pyplot as plt


def plothist(hist, bin_edges, baseline=None, histtype="bar", axis=None, **kwargs):
    """Plot a histogram from the hist and bin edges as returned by numpy.histogram.
    """
    if axis is None:
        axis = plt.gca()

    if not histtype == "bar":
        raise NotImplementedError
    zero = np.zeros(1, dtype=hist.dtype)
    x = np.concatenate([bin_edges, [bin_edges[-1]]])
    if baseline is None:
        y = np.concatenate([zero, hist, zero])
        axis.step(x, y, where="pre", **kwargs)
    else:
        y1 = np.concatenate([zero, baseline, zero])
        y2 = np.concatenate([zero, baseline + hist, zero])
        axis.fill_between(x, y1, y2, step="pre", **kwargs)
