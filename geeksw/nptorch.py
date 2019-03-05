import numpy as np
import torch


def _wrap_numpy_torch(numpy_f, torch_f):
    def wrapped_f(*args, **kwargs):
        for x in args:
            if isinstance(x, torch.Tensor):
                return torch_f(*args, **kwargs)
        return numpy_f(*args, **kwargs)

    return wrapped_f


exp = _wrap_numpy_torch(np.exp, torch.exp)
cos = _wrap_numpy_torch(np.cos, torch.cos)
sin = _wrap_numpy_torch(np.sin, torch.sin)
tan = _wrap_numpy_torch(np.tan, torch.tan)
sqrt = _wrap_numpy_torch(np.sqrt, torch.sqrt)
