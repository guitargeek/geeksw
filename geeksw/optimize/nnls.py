import numpy as np
import numpy.ma as ma


def nnls(A, b, maxiter=None, eps=1e-11):
    """
    Solve ``argmin_x || Ax - b ||_2`` for ``x>=0``, i.e. non-negative least squares.
    Parameters
    ----------
    A : ndarray
        Matrix ``A`` as shown above.
    b : ndarray
        Right-hand side vector.
    maxiter: int, optional
        Maximum number of iterations, optional.
        Default is ``3 * A.shape[1]``.
    eps: float, optional
        Tolerance parameter for stopping criterion, optional.
        Default is ``1e-11``.
    Returns
    -------
    x : ndarray
        Solution vector.
    Notes
    -----
    This implements the algorithm described on Wikipedia, which in turn references a book for 1987.
    The same algorithm is also implemented in Fortran, and available from Python via ``scipy.optimize.nnls``.
    The scipy version is therefore about 4 times faster, but has the disadvantage of being less native to Python.
    References
    ----------
    https://en.wikipedia.org/wiki/Non-negative_least_squares
    Lawson C., Hanson R.J., (1987) Solving Least Squares Problems, SIAM
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.nnls.html
    """
    m, n = A.shape
    x = np.zeros(n)
    P = []
    Z = list(range(n))
    k = 0

    if maxiter is None:
        maxiter = 3 * m

    while True:
        if k == maxiter:
            return x

        w = np.matmul(A.T, (b - np.matmul(A, x)))
        if Z == [] or np.all(w[Z] <= eps):
            return x

        while True:

            t = np.argmax(ma.masked_array(w, mask=[not i in Z for i in range(n)]))
            P.append(t)
            Z.remove(t)
            Ap = A.copy()
            Ap[:, Z] = 0

            z = np.linalg.lstsq(Ap, b, rcond=None)[0]

            if np.all(z[P] > 0):
                x = z
                break

            alpha = np.min(ma.masked_array(x / (x - z), mask=[not i in P or z[i] > 0 for i in range(n)]))
            x = x + alpha * (z - x)

            T = np.where(x == 0.0)[0]
            Z = [z for z in set(Z + P) if z in Z or z in P and z in T]
            P = [p for p in P if not p in T]

        k = k + 1
