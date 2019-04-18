import numpy as np
from scipy.special import erf, erfc, gamma


def gaus(x, A, mu, sigma):
    """A scaled normal distribution.
    """
    return A * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def crystalball(x, a, n, xb, sig):
    """A scaled crystal ball distribution, i.e. a Gaussian with a power law for the left tail.
    """
    x = x + 0j
    if a < 0:
        a = -a
    if n < 0:
        n = -n
    aa = abs(a)
    A = (n / aa) ** n * np.exp(-aa ** 2 / 2)
    B = n / aa - aa
    C = n / aa * 1 / (n - 1) * np.exp(-aa ** 2 / 2)
    D = np.sqrt(np.pi / 2) * (1 + erf(aa / np.sqrt(2)))
    N = 1.0 / (sig * (C + D))
    total = 0.0 * x
    total += ((x - xb) / sig > -a) * N * np.exp(-(x - xb) ** 2 / (2.0 * sig ** 2))
    total += ((x - xb) / sig <= -a) * N * A * (B - (x - xb) / sig) ** (-n)
    return total.real
    try:
        return total.real
    except:
        return total
    return total


def gausexp(x, N, mu, sigma, k):
    """A scaled probability density function for a Gaussian with an exponential tail on the left.
    """
    if k < 0:
        k = -k

    total = 0.0 * x
    total += ((x - mu) / sigma > -k) * N * np.exp(-(x - mu) ** 2 / (2.0 * sigma ** 2))
    total += ((x - mu) / sigma <= -k) * N * np.exp(k ** 2 / 2.0 + k * ((x - mu) / sigma))

    return total


def cbexgaus(m, m0, sigma, alpha, n, sigma2, left_tail):
    """Convolution fix + exponential tail on the left.

    It is not clear yet what this actually is. This distribution was obtained from https://github.com/fcouderc/egm_tnp_analysis/blob/master/libCpp/RooCBExGaussShape.h and is used to model signal distributions in EGM tag and probe studies.
    """
    t = (m - m0) / sigma
    t0 = (m - m0) / sigma2
    abs_alpha = abs(alpha)
    abs_n = abs(n)

    if left_tail >= 0:
        return (
            (t > 0) * np.exp(-0.5 * t0 * t0)
            + np.logical_and(t > -abs_alpha, t <= 0) * np.exp(-0.5 * t * t)
            + (t <= -abs_alpha) * np.exp(-0.5 * abs_alpha ** 2) * np.exp(n * (t + abs_alpha))
        )
    else:
        return (
            (t < 0) * np.exp(-0.5 * t * t)
            + np.logical_and(t < abs_alpha, t >= 0) * np.exp(-0.5 * t0 * t0)
            + (t >= abs_alpha)
            * (abs_n / abs_alpha) ** abs_n
            * np.exp(-0.5 * abs_alpha ** 2)
            / (abs_n / abs_alpha - abs_alpha + t0) ** absN
        )


def cmsshape(x, alpha, beta, gamma, peak):
    """Probability density function for exponential decay
    distributions at high mass beyond the pole position.

    Defines a probability density function which has exponential decay 
    distribution at high mass beyond the pole position (say, Z peak)  
    but turns over (i.e., error function) at low mass due to threshold 
    effect. We use this to model the background shape in Z->ll invariant 
    mass.
    """
    e = erfc((alpha - x) * beta)
    u = (x - peak) * gamma

    return (u < -70) * e * 1e20 + np.logical_and(u >= -70, u <= 70) * e * np.exp(-u)


def grindhammer(t, alpha, beta, E):
    """Gamma distribution to fit longitudial shower shapes in particles calorimeters.

    See equation 2 in https://arxiv.org/pdf/hep-ex/0001020v1.pdf
    """
    return E * ((beta * t) ** (alpha - 1) * beta * np.exp(-beta * t)) / scipy.special.gamma(alpha)


def p0gausexp(x, y, yerr):

    # Get mu
    mu_idx = np.argmax(y)
    mu = x[mu_idx]

    # get index ranges left and right of mu
    left_range = np.arange(len(x))[:mu_idx]
    right_range = np.arange(len(x))[mu_idx + 1 :]

    left_range = left_range[-len(right_range) :]
    right_range = right_range[::-1]

    x_tail = x[left_range]
    y_left = y[left_range]
    y_right = y[right_range]
    yerr_left = yerr[left_range]
    yerr_right = yerr[right_range]

    k = (np.sum(np.sqrt((y_left - y_right) ** 2 / (yerr_left * yerr_right)) < 1.0) + 0.5) * (x[1] - x[0])

    N = y[mu_idx]

    x_mirror = np.concatenate([x[left_range], [mu], x[right_range]])
    y_mirror = np.concatenate([y[right_range], [y[mu_idx]], y[right_range]])

    sigma = np.sqrt(np.average((x_mirror - mu) ** 2, weights=y_mirror))
    k = k / sigma

    return [N, mu, sigma, k]
