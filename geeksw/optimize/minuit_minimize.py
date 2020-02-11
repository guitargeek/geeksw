from iminuit import Minuit
from iminuit.util import make_func_code

from collections import namedtuple

MinuitResult = namedtuple("MinuitResult", ["values", "errors", "f_val"])


def minuit_minimize(func, param_names, starting_params, starting_errors, fixed_params=dict(), errordef=0.5):
    """ Minimizes a functin using iMinuit.
    
    Args:
        func (function): Function to mimimize.
                         Should only take a dictionary of parameters as input.
        param_names (list of str): The names of the parameters to pass to the function.
        starting_params (list of float): Starting values of the parameters for the minimization.
        starting_errors (list of float): Starting errors of the parameters for the minimization,
                                         i.e. the initial minimization step size.
        fixed_params (dict of str : float): Fill this dictionary with the parameters you want
                                            to fix in this mimimization and their values.
        errordef (float, default value 0.5): Forwarded to the Minuit instance.
                                             Has to be 0.5 for negative log-likelihood functions
                                             and 1 for least-squares functions.

    Returns:
        MinuitResult: It contains the optimized parameter values, uncertainties and the minimized function value.
    """

    assert len(param_names) == len(starting_params)
    assert len(param_names) == len(starting_errors)

    floating_param_names = []
    floating_starting_params = []
    floating_starting_errors = []

    for i, name in enumerate(param_names):
        if name in fixed_params:
            continue
        floating_param_names.append(name)
        floating_starting_params.append(starting_params[i])
        floating_starting_errors.append(starting_errors[i])

    def fcn(*param_values):
        floating_params = {name: value for name, value in zip(floating_param_names, param_values)}
        return func(**floating_params, **fixed_params)

    fcn.func_code = make_func_code(floating_param_names)

    minuit_instance = Minuit(
        fcn,
        errordef=errordef,
        **{name: x for name, x in zip(floating_param_names, floating_starting_params)},
        **{"error_" + name: x for name, x in zip(floating_param_names, floating_starting_errors)}
    )

    minuit_instance.migrad()
    minuit_instance.hesse()

    values = minuit_instance.values

    return MinuitResult(values, minuit_instance.errors, fcn(*values.values()))
