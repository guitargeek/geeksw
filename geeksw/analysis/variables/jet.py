import numpy
import pandas
import awkward

from .. import utils


def btag(df, tagger, working_point):

    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X

    taggers = {
        "DeepCSV": {"col_name": "Jet_btagDeepB", "working_points": {"loose": 0.1522, "medium": 0.4941, "tight": 0.8001}}
    }

    working_points = list(taggers["DeepCSV"]["working_points"].keys())

    if not tagger in taggers:
        raise ValueError('tagger has to be any of "' + '", "'.join(taggers.keys()) + '".')

    if not working_point in working_points:
        raise ValueError('working_point has to be any of "' + '", "'.join(working_points) + '".')

    tagger = taggers[tagger]

    return df[tagger["col_name"]] > tagger["working_points"][working_point]


def n_bjets(df, tagger, working_point, pt_threshold=20.0, max_eta=2.4):

    b_tagged = btag(df, tagger, working_point).values

    is_b_jet = numpy.logical_and.reduce(
        [b_tagged, df["Jet_pt"].values >= pt_threshold, numpy.abs(df["Jet_eta"]) < max_eta]
    )

    event = df.index.get_level_values(0).values
    unique_event = utils.unique_keep_order(event)

    jagged_arr = awkward.JaggedArray.fromcounts(utils.count(event), is_b_jet)

    series = pandas.Series(jagged_arr.sum(), index=unique_event)
    series.index.name = "event"

    return series
