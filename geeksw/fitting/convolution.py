import numpy as np


def conv(f, g):
    def h(x):
        """Input x has to be equidistant!
        """
        # If the support of f or g extends outside x,
        # we have to evaluate the functions also outside x
        # to get the values of the convolution for all x.
        n = len(x)
        d = x[1] - x[0]

        x_ext = np.concatenate([x[-n:] - n * d, x, x[:n] + n * d])
        m = len(x_ext)

        x_ext_tiled = np.tile(x_ext, (m, 1))
        distance_matrix = x_ext_tiled - x_ext_tiled.T

        res = np.sum(g(-distance_matrix) * np.tile(f(x_ext), (m, 1)), axis=1) * d

        return res[n:-n]

    return h


from scipy.signal import fftconvolve


def fconv(f, g):
    def h(x):
        """Input x has to be equidistant!
        """
        # Do some trickery to evaluate the convolution at the desired x-values.
        n = len(x)
        d = x[1] - x[0]
        x_ext = np.concatenate([x[-n // 2 :] - n * d, x, x[: n // 2] + n * d])
        res = fftconvolve(f(x_ext), g(x_ext), mode="full") * (x_ext[1] - x_ext[0])
        return np.interp(x, x_ext * 2, res[::2])

    return h
