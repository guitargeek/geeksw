import numpy as np
import pandas as pd

import inspect

import scipy.special
import scipy.stats

from collections import namedtuple

from geeksw.optimize.minuit_minimize import minuit_minimize

def _get_nuisance_parameter_name(func):
    if hasattr(func, "nuisance_parameter_name"):
        return func.nuisance_parameter_name
    args = inspect.getfullargspec(func).args
    assert len(args) == 2
    assert args[1] == "datacard"
    return args[0]


def make_nll_func(datacard, signal_strengths, nuisances=[], observations=None):

    if observations is None:
        observations = datacard.sum(axis=1)

    def nll_term(s, b, n):
        return (s + b) - n * np.log(s + b)

    signal_columns = "+".join(signal_strengths.values()).split("+")
    background_columns = [c for c in datacard.columns if not c in signal_columns]

    nuisance_param_names = [_get_nuisance_parameter_name(nuis) for nuis in nuisances]

    def nll_func(**params):

        df = datacard.copy(deep=True)

        nll = 0.0

        for nuisance, param_name in zip(nuisances, nuisance_param_names):
            df, constraint = nuisance(params[param_name], df)
            nll += constraint

        s = pd.DataFrame({key: params[key] * df.eval(signal_strengths[key]) for key in signal_strengths}).sum(axis=1)
        b = df[background_columns].sum(axis=1)

        return nll + nll_term(s, b, observations).sum()

    return nll_func


AsymptoticDiscoveryFitResult = namedtuple("AsymptoticDiscoveryFitResult", ["df_mu", "df_nuisance", "nll_value"])


def asymptotic_discovery_fit(datacard, signal_strengths=None, nuisances=[], observations=None, fixed_params={}):

    nll_func = make_nll_func(datacard, signal_strengths, nuisances, observations)

    nuisance_param_names = [_get_nuisance_parameter_name(nuis) for nuis in nuisances]
    signal_strength_param_names = list(signal_strengths.keys())
    param_names = signal_strength_param_names + nuisance_param_names
    n_params = len(param_names)
    starting_params = [1.1] * n_params
    starting_errors = [0.1] * n_params

    values, errors, nll = minuit_minimize(
        nll_func, param_names, starting_params, starting_errors, fixed_params=fixed_params
    )

    df = pd.DataFrame(dict(value=list(values.values()), error=list(errors.values())), index=param_names)
    df = df.eval("precision=error/value")

    def set_elem_to_zero(a, name):
        b = dict(**a)
        b[name] = 0.0
        return b

    def two_dnnl(name):
        fixed_params_plus_one = dict(**fixed_params)
        fixed_params_plus_one[name] = 0.0
        if len(fixed_params_plus_one) == len(param_names):
            null_nll = nll_func(**fixed_params_plus_one)
        else:
            null_nll = minuit_minimize(
                nll_func, param_names, starting_params, starting_errors, fixed_params=fixed_params_plus_one
            ).f_val
        ll_0 = -null_nll
        ll_best_fit = -nll_func(**values)
        return -2 * (ll_0 - ll_best_fit)

    df_mu = df.loc[signal_strength_param_names]
    df_nuisance = df.loc[nuisance_param_names]

    df_mu["significance"] = np.array(list(map(two_dnnl, signal_strength_param_names)))

    # if the error was NaN because the parameter was fixed, then we also set the significance or p_value to NaN
    df_mu.loc[df_mu["error"].isna(), "significance"] = np.nan

    df_mu["significance"] = np.sqrt(df_mu["significance"])
    df_mu["p_value"] = 0.5 * (1.0 + scipy.special.erf(-df_mu["significance"] / np.sqrt(2.0)))

    return AsymptoticDiscoveryFitResult(df_mu, df_nuisance, nll)


# Additional negative log-likelihood terms commonly used for nuisance parameters


def normal_penalty(x, relative_uncertainty):
    sigma = relative_uncertainty
    return -scipy.stats.norm.logpdf(x, scale=sigma, loc=1.0)


def lognormal_penalty(x, relative_uncertainty, associate_best_estimate_with="median"):
    kappa = relative_uncertainty + 1.0
    sigma = np.log(kappa)
    if associate_best_estimate_with == "median":
        mu = 0
    if associate_best_estimate_with == "mean":
        mu = -(sigma ** 2.0) / 2
    if associate_best_estimate_with == "mode":
        mu = relative_uncertainty ** 2.0
    return -scipy.stats.lognorm.logpdf(x, sigma, loc=mu)


def gamma_penalty(x, relative_uncertainty):
    a = 1.0 / relative_uncertainty ** 2
    b = 1.0 / relative_uncertainty ** 2 + 1
    return -scipy.stats.gamma.logpdf(a * x, b)
