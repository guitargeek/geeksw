import awkward
import numpy
import pandas
import numpy
import awkward
import uproot_methods
import pandas


def is_first_in_event(event):
    return numpy.concatenate([[1], event[1:] != event[:-1]])


def count(arr):
    if not isinstance(arr, (pandas.Series, pandas.DataFrame)):
        return numpy.diff(numpy.where(numpy.concatenate([is_first_in_event(arr), [1]]))[0])
    counts = count(arr.index.get_level_values(0).values)

    series = pandas.Series(counts, index=unique_keep_order(arr.index.get_level_values(0).values))
    series.index.name = "event"

    return series


def lorentz_vector_array(df, counts=None):
    if counts is None:
        counts = count(df)
    particle = df.columns[0].split("_")[0]
    kinematics_columns = ["pt", "eta", "phi", "mass"]
    pt, eta, phi, m = (
        awkward.JaggedArray.fromcounts(counts, df[particle + "_" + c].values) for c in kinematics_columns
    )
    return uproot_methods.TLorentzVectorArray.from_ptetaphim(pt, eta, phi, m)


def indices_in_event(event):
    r = numpy.arange(len(event))
    t = is_first_in_event(event) * r
    w = numpy.where(t)[0]
    t[w[1:]] -= t[w[:-1]]
    return r - numpy.cumsum(t)


def jagged_zeros(counts, dtype=float):
    content = numpy.zeros(numpy.sum(counts), dtype=dtype)
    return awkward.JaggedArray.fromcounts(counts, content)


def jagged_zeros_like(a, dtype=None):
    return awkward.JaggedArray(a.starts, a.stops, numpy.zeros_like(a.flatten(), dtype=dtype))


def unique_keep_order(event):
    counts = count(event)
    a = awkward.JaggedArray.fromcounts(counts, event)
    return a[:, 0]


def to_jagged(series):
    counts = count(series.index.get_level_values("event"))
    return awkward.JaggedArray.fromcounts(counts, series.values)


def events(df):
    if df.index.nlevels == 1:
        return df.index.get_level_values("event")

    counts = count(df.index.get_level_values("event"))
    return awkward.JaggedArray.fromcounts(counts, df.index.get_level_values("event"))


def select_objects(df, object_indices, invert=False):
    event = df.index.get_level_values("event").values

    counts = utils.count(event)

    unique_events = utils.unique_keep_order(event)

    mask = utils.jagged_zeros(counts, dtype=numpy.bool)

    if not numpy.in1d(object_indices.index.values, unique_events).all():
        raise ValueError("Some objects you want to select are not in the DataFrame.")

    em = numpy.in1d(unique_events, object_indices.index.values)

    a = awkward.JaggedArray.fromcounts(utils.count(object_indices.index), object_indices.values)

    t = awkward.JaggedArray.fromcounts(counts, df.index.get_level_values(1).values)

    if len(a.flatten()) != len(a):
        raise NotImplementedError

    mask[em][t[em] == a.flatten()] = True

    mask = mask.flatten()

    return df[~mask] if invert else df[mask]


def unselect_objects(df, object_indices):
    return select_objects(df, object_indices, invert=True)


def unique_events(df):
    return utils.unique_keep_order(df.index.get_level_values("event").values)


def add_column(df, series, column_name, default_value):
    df[column_name] = default_value
    event = series.index.get_level_values("event")
    df.loc[event, column_name] = series
    return df


def count_if(df, query):

    event = df.index.get_level_values("event").values
    unique_event = utils.unique_keep_order(event)

    jagged_arr = awkward.JaggedArray.fromcounts(utils.count(event), df.eval(query).values)

    series = pandas.Series(jagged_arr.sum(), index=unique_event)
    series.index.name = "event"

    return series


def array(series):
    counts = utils.count(series)
    a = awkward.JaggedArray.fromcounts(counts, series)
    return a
