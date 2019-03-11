import numpy as np
from scipy.special import erf


def gaus(x, A, mu, sigma):
    return A * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def crystalball(x, a, n, xb, sig):
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
    if k < 0:
        k = -k

    total = 0.0 * x
    total += ((x - mu) / sigma > -k) * N * np.exp(-(x - mu) ** 2 / (2.0 * sigma ** 2))
    total += ((x - mu) / sigma <= -k) * N * np.exp(k ** 2 / 2.0 + k * ((x - mu) / sigma))

    return total
