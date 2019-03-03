import torch


def wrap_jac(f, dtype=torch.float):
    def jac(x, *p):
        n = len(x)
        p = np.array(p).repeat(n).reshape(len(p),n)
        p = torch.tensor(p, dtype=dtype, requires_grad=True)
        x = torch.tensor(x, dtype=dtype)
        y = f(x, *p)
        y.sum().backward()
        return p.grad.t()
    return jac
