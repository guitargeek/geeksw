import numpy as np
import pandas as pd


def very_loose_id(df):

    # adapted from wvzBabyMaker::isPt10VeryLooserThanPOGVetoMuon(int idx)
    # https://github.com/sgnoohc/WVZBabyMaker/blob/92107208e6a84a62ea7e9bc1f333d38bd3264a23/babymaker/wvzBabyMaker.cc#L585

    is_ee = df["Muon_eta"] > 1.497

    return df[
        np.logical_and.reduce(
            [
                df["Muon_mediumId"],
                df["Muon_pt"] > 10.0,
                df["Muon_eta"].abs() < 2.4,
                df["Muon_dz"].abs() < 0.1 + is_ee * 0.1,
                df["Muon_dxy"].abs() < 0.05 + is_ee * 0.05,
            ]
        )
    ]


def isLooseMuonPOG(mus):
    # https://github.com/cmstas/CORE/blob/master/MuonSelections.cc

    mask = np.logical_and(mus["Muon_isPFcand"], np.logical_or(mus["Muon_isGlobal"], mus["Muon_isTracker"]))

    return pd.Series(mask, index=mus.index)
