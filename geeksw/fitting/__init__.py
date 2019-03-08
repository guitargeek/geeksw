def leastsq(func, x0, Dfun=None, lam0=0.1, nu=2, ftol=1.49012e-08, maxfev=2000, epsfcn=None):
    
    dtype = x0.dtype
    
    if epsfcn is None:
        epsfcn = np.finfo(dtype).eps
    
    n = len(x0)
    lam = np.eye(n) * lam0
    
    x = x0
            
    def get_res(x):
        return np.sum(func(x)**2, axis=-1)
    
    res = get_res(x)
    N = len(res)
    
    if Dfun is None:
        def Dfun(x):
            fvec = func(x)
            devi = np.empty((n,)+fvec.shape,dtype=dtype)
            for i in range(n):
                eps = np.zeros_like(x, dtype=dtype)
                eps[i] = np.sqrt(epsfcn)
                devi[i] = (func(x + eps) - fvec)
            devi /= -np.sqrt(epsfcn)
            devi = np.moveaxis(devi, 0, -1)
            
            return devi
    
    lam = np.tile(lam, N).T.reshape((N,)+lam.shape)
    nu = np.ones_like(lam) * nu
    
    def foo(a):
        return np.repeat(a, n**2).reshape(lam.shape)
    
    def bar(a):
        return np.repeat(a, n).reshape(lam.shape[:-1])

    iter = 0
    
    isdone = np.zeros(N, dtype=np.bool)
            
    while True:
        
        if iter >= maxfev:
            raise ValueError("Fit did not converge")
        
        fvec = func(x)
        J = Dfun(x)
        JT = np.swapaxes(J, -2, -1)
        JTJ = np.matmul(JT, J)

        JTfvec = np.einsum("...ij,...j", JT, fvec)
        
        delta = np.linalg.solve(JTJ + lam, JTfvec)
        delta_nu = np.linalg.solve(JTJ + lam/nu, JTfvec)
                
        res_prev = res
        res = get_res(x + delta.T)
        res_nu = get_res(x + delta_nu.T)
        
        mask1 = np.logical_or(res < res_prev, res_nu < res_prev)
        mask2 = np.logical_and(mask1, res_nu < res)
        
        lam = lam + lam * (nu - 1) * foo(~mask1) + lam * (1./nu - 1) * foo(mask2)
        res = res * ~mask2 + res_nu * mask2
        delta = delta * bar(~mask2) + delta_nu * bar(mask2)
                
        isdone = np.logical_or(np.logical_and(mask1, res_prev - res < ftol), isdone)
        
        if isdone.all():
            break
        
        x = x + delta.T * np.logical_and(mask1, ~isdone)

        iter += 1


    return x.T, None


def curve_fit(f, x, y, p0):
    
    if len(x.shape) == 1:
        x = x[np.newaxis,:]
        y = y[np.newaxis,:]
        p0 = p0[:,np.newaxis]
    
    n = x.shape[-1]
    
    def func(p):
        p = np.repeat(p, n).reshape(p.shape + (n,))
        return y - f(x, *p)
    
    popt, pcov = leastsq(func, p0)
    if len(popt.shape) == 2 and popt.shape[0] == 1:
        return popt[0], pcov
    return popt, pcov
