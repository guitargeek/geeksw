"""
Reweighting-related functions
"""

import numpy as np


def reweight1d(a, reference=1, bins=10, get_w_ref=False):
    """Get weights for a 1d array to match the distribution of another array.

    Args:
        a (array_like): The array with the variable we want to reweight.
        reference (scalar or array_like): Either a scalar value if you want to
            reweight to a flat distribution, or an array for extracting the
            distribution to match.
        bins (int or sequence of scalars or str, optional) If `bins` is an int,
            it defines the number of equal-width bins in the given range (10,
            by default). If `bins` is a sequence, it defines the bin edges,
            including the rightmost edge, allowing for non-uniform bin widths.
            If `bins` is a string, it defines the method used to calculate the
            optimal bin width, as defined by `numpy.histogram_bin_edges`.
        get_w_ref (bool, optinal): If set to true, weights for the reference
            distribution will also be returned.

    Returns:
        w (array of dtype float): The weights for the input array to match the
            reference arrays distribution.
        w_ref (darray of dtype float, optional) The weights for the reference
            array, with are 1 in the binning and 0 outside.

    Notes:
        If an entry of `a` falls out of the binning range or the refrence has
        zero entries in that bin, its weight will be zero.

    Examples:
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>>
        >>> # Exponential background and Gaussian signal
        >>> bkg = np.random.exponential(scale=1.0, size=n)
        >>> sig = np.random.normal(loc=2.0, scale=1.0, size=n)
        >>>
        >>> # Calculate weights
        >>> w_sig, w_bkg = reweight1d(sig, bkg, bins=200)

        >>> # Plot histograms
        >>> bins = np.linspace(-2, 7, 200)
        >>> plt.hist(sig, bins=bins, weights=w_sig, label="sig")
        >>> plt.hist(bkg, bins=bins, weights=w_bkg, label="bkg")
        >>> plt.legent(loc="upper right")
        >>> plt.show()
    """

    h, bin_edges = np.histogram(a, bins=bins)
    h = np.array(h, dtype=np.float)

    if hasattr(reference, "__len__"):
        h_ref, _ = np.histogram(reference, bins=bin_edges)
        h_ref = np.array(h_ref, dtype=np.float)
    else:
        h_ref = reference

    h_w = np.divide(h_ref, h, out=np.zeros_like(h), where=h != 0)
    h_w = np.concatenate([[0.0], h_w, [0.0]])

    h_w[np.isinf(h_w)] = 0

    w = h_w[np.clip(np.digitize(a, bin_edges), 0, len(bin_edges))]

    if get_w_ref:
        w_ref = h_w[np.clip(np.digitize(reference, bin_edges), 0, len(bin_edges))] > 0
        return w, np.array(w_ref, dtype=np.float)
    else:
        return w
