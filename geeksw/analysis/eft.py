import pandas as pd
import numpy as np

wwzz_dim8_operators = [
    "FS0",
    "FS1",
    "FM0",
    "FM1",
    "FM2",
    "FM3",
    "FM4",
    "FM5",
    "FM6",
    "FM7",
    "FT0",
    "FT1",
    "FT2",
    "FT5",
    "FT6",
    "FT7",
]


def get_df_mg_reweighting_info(mg_reweighting_title):
    import io

    return pd.read_csv(io.StringIO(mg_reweighting_title), lineterminator=";", skiprows=1)


def get_df_mg_reweighting(gen_weight, mg_reweighting, mg_reweighting_title, standard_model=None):

    df_info = get_df_mg_reweighting_info(mg_reweighting_title)
    mg_reweighting = gen_weight * mg_reweighting
    df = pd.DataFrame(mg_reweighting.flatten().reshape((len(mg_reweighting), len(mg_reweighting[0]))))
    df.columns = df_info["id"].values

    if standard_model is None:
        norm = np.sum(gen_weight)
    else:
        norm = df[standard_model].sum()

    return df / norm


class EFTReweighter(object):
    def __init__(self, gen_weight, mg_reweighting, mg_reweighting_title, xsec=1.0, lumi=1.0):
        def get_coefficients(op):
            v = np.array([-1.0, 0, 1])
            w = df_weights[[f"EFT__{op}_m1", "EFT__SM", f"EFT__{op}_1"]].values
            x = np.tile(np.vstack([v ** 2, v, np.ones_like(v)]).T, (len(w), 1, 1))
            return np.linalg.solve(x, w)

        df_weights = get_df_mg_reweighting(gen_weight, mg_reweighting, mg_reweighting_title, standard_model="EFT__SM") * xsec * lumi

        self.coef_ = {}

        for op in wwzz_dim8_operators:
            self.coef_[op] = get_coefficients(op)

    def __call__(self, operator, value, subtract_sm=False):

        if hasattr(value, "__len__"):
            dtype = object
        else:
            if value == 0.0:
                # if the value is zero, we deal with SM and can just take the offsets of any operator,
                # which should be the same
                if subtract_sm:
                    return np.zeros_like(self.coef_["FT0"][:, 2])
                return self.coef_["FT0"][:, 2]
            dtype = type(value)

        x = np.array([value ** 2, value, 1.0], dtype=dtype)
        weights = np.matmul(self.coef_[operator], x)

        if subtract_sm:
            return weights - self.coef_["FT0"][:, 2]

        return weights
