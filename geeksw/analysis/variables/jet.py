import numpy
import pandas
import awkward

from .. import utils


def identification(df, working_point):
    if working_point == "tight":
        return df["Jet_jetId"] & 2 > 0
    if working_point == "loose":
        return df["Jet_jetId"] & 1 > 0
    raise ValueError('The working_point parameter must either be "loose" or "tight".')


def btag(df, tagger, working_point, year):
    # https://twiki.cern.ch/twiki/bin/view/CMS/BtagRecommendation

    if year == 2016:
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation2016Legacy
        taggers = {
            "DeepCSV": {"col_name": "Jet_btagDeepB", "working_points": dict(loose=0.2217, medium=0.6321, tight=0.8953)},
            "DeepJet": {
                "col_name": "Jet_btagDeepFlavB",
                "working_points": dict(loose=0.0614, medium=0.3093, tight=0.7221),
            },
        }
    elif year == 2017:
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation94X
        taggers = {
            "CSVv2": {"col_name": "Jet_btagCSVV2", "working_points": dict(loose=0.5803, medium=0.8838, tight=0.9693)},
            "DeepCSV": {"col_name": "Jet_btagDeepB", "working_points": dict(loose=0.1522, medium=0.4941, tight=0.8001)},
            "DeepJet": {
                "col_name": "Jet_btagDeepFlavB",
                "working_points": dict(loose=0.0521, medium=0.3033, tight=0.7489),
            },
        }
    elif year == 2018:
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation102X
        taggers = {
            "DeepCSV": {"col_name": "Jet_btagDeepB", "working_points": dict(loose=0.1241, medium=0.4184, tight=0.7527)},
            "DeepJet": {
                "col_name": "Jet_btagDeepFlavB",
                "working_points": dict(loose=0.0494, medium=0.2770, tight=0.7264),
            },
        }
    else:
        raise ValueError("Year " + str(year) + " unsupported.")

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
