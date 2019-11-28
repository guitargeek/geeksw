from math import log10, floor


def represent_value_and_uncert(value, uncert, n_significant_digits=2):
    if uncert == 0.0:
        return f"{value} ± {uncert}"
    n_digits = -int(floor(log10(abs(uncert)))) - 1 + n_significant_digits
    return f"{round(value, n_digits)} ± {round(uncert, n_digits)}"


def format_errors_in_df(df, error_suffix="_err"):
    df = df.copy(deep=True)
    for col in df:
        if col + error_suffix in df:
            df[col] = list(map(lambda x: represent_value_and_uncert(*x), zip(df[col], df[col + error_suffix])))
            df = df.drop(col + error_suffix, axis=1)
    return df
