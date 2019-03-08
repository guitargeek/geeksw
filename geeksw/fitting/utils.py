import torch
import numpy as np


def wrap_jac(f, dtype=torch.float):
    def jac(x, *p):
        n = len(x)
        p = torch.tensor(p, dtype=dtype, requires_grad=True)
        x = torch.tensor(x, dtype=dtype)
        y = f(x, *p)
        y.sum().backward()
        return np.moveaxis(p.grad.detach().numpy(), 0, -1)

    return jac
