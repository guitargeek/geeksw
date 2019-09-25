import awkward
import numpy
import pandas

from .. import utils


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
