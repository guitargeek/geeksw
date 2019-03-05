import torch


def torch_fit(f, xdata, ydata, p0=None, rounds=10000, learning_rate=1e-3):
    """Experimental function to fit data with gradient descent like neural networks.
    """

    if p0 is None:
        # determine number of parameters by inspecting the function
        from scipy._lib._util import getargspec_no_self as _getargspec

        args, varargs, varkw, defaults = _getargspec(f)
        if len(args) < 2:
            raise ValueError("Unable to determine number of fit parameters.")
        n = len(args) - 1

    dtype = torch.float
    x = torch.tensor(xdata, dtype=dtype)
    y = torch.tensor(ydata, dtype=dtype)

    if p0 is None:
        p = torch.randn(n, dtype=dtype, requires_grad=True)
    else:
        p = torch.tensor(p0, dtype=dtype, requires_grad=True)

    optimizer = torch.optim.Adam([p], lr=learning_rate)

    for t in range(rounds):
        loss = (f(x, *p) - y).pow(2).sum()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    popt = p.detach().numpy()
    pcov = None

    return popt, pcov
