from math import log10, floor


def represent_value_and_uncert(value, uncert, n_significant_digits=2, plus_minus="±"):
    if uncert == 0.0:
        return f"{value} {plus_minus} {uncert}"
    n_digits = -int(floor(log10(abs(uncert)))) - 1 + n_significant_digits
    return f"{round(value, n_digits)} {plus_minus} {round(uncert, n_digits)}"


def format_errors_in_df(df, error_column_suffix="_err", plus_minus="±"):
    df = df.copy(deep=True)
    for col in df:
        col_err = col + error_column_suffix
        if col_err in df:
            df[col] = list(
                map(lambda x: represent_value_and_uncert(*x, plus_minus=plus_minus), zip(df[col], df[col_err]))
            )
            df = df.drop(col_err, axis=1)
    return df
