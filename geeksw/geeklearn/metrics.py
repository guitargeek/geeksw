from sklearn.metrics import roc_curve
import numpy as np


def calibration_curve(y_true, y_score, sample_weight=None, curve_type="stitched"):
    """Computes the empirical test curve that checks if a classifier score is
    well-calibrated to the be the likelihood.
    """
    allowed_curve_types = ["forward", "backward", "stitched"]
    if not curve_type in allowed_curve_types:
        raise ValueError("Type has to be either " + ", ".join(allowed_curve_types))

    G, F, x = (a[:-1][::-1] for a in roc_curve(y_true, y_score, drop_intermediate=False, sample_weight=sample_weight))

    def _curve(backward=False):

        sums = (F + G)[:-1] * np.diff(x)
        direction = 1 - 2 * backward

        integrals = np.cumsum(sums[::direction])[::direction]
        C = np.zeros(len(x) - 1, dtype=np.float) + backward
        np.divide(F[1:] + direction * integrals, (F + G)[1:], where=(F + G)[1:] > 0, out=C)

        return x[1:-1], C[:-1]

    if curve_type == "forward":
        F = 1.0 - F
        G = 1.0 - G
        return _curve()

    if curve_type == "backward":
        return _curve(backward=True)

    _, C2 = _curve(backward=True)
    F = 1.0 - F
    G = 1.0 - G
    x, C1 = _curve()

    m = len(x) // 2

    return x, np.concatenate([C2[:m], C1[m:]])
