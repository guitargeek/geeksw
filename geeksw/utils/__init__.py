import numpy as np


def rmseff(x, c=0.68):
    """Compute half-width of the shortest interval
    containing a fraction 'c' of items in a 1D array.
    """
    x = np.sort(x, kind="mergesort")
    m = int(c * len(x)) + 1
    return np.min(x_sorted[m:] - x_sorted[:-m]) / 2.0


def inv_mass_expr(expr):

    # split up expression
    x = []
    s = "+"
    for i in range(len(expr)):
        if expr[i] == "-":
            s = "-"
        if expr[i] == "(":
            tmp = expr[i + 1 : i + expr[i:].find(")")]
            tmp = tmp.split(",")
            # If there is no entry for the energy,
            # just assume its a massless particle
            if len(tmp) == 3:
                tmp = [tmp[0] + "*cosh(" + tmp[1] + ")"] + tmp
            x.append({"e": tmp[0], "pt": tmp[1], "eta": tmp[2], "phi": tmp[3], "sign": s})
            s = "+"

    # Build the expression for the invariant mass
    out = "(("
    for xi in x:
        out += "{}{}".format(xi["sign"], xi["e"])
    out += ")**2"
    out += " - ("
    for xi in x:
        out += "{}{}*cos({})".format(xi["sign"], xi["pt"], xi["phi"])
    out += ")**2"
    out += " - ("
    for xi in x:
        out += "{}{}*sin({})".format(xi["sign"], xi["pt"], xi["phi"])
    out += ")**2"
    out += " - ("
    for xi in x:
        out += "{}{}*sinh({})".format(xi["sign"], xi["pt"], xi["eta"])
    out += ")**2"
    out += ")**0.5"

    return out


def gaussian_smearing(arr, percent):

    return arr * np.random.normal(1.0, percent / 100.0, arr.shape)
