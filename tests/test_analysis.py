import unittest
import uproot
import numpy as np

import geeksw.analysis.genpart as genpart


def count_leptons_from_weak_boson_decays(nano_file):
    events = uproot.open(nano_file)["Events"]
    df = events.pandas.df([b"GenPart_genPartIdxMother", b"GenPart_pdgId"])
    df["GenPart_pdgIdMother"] = genpart.get_pdgIdMother(df)

    df = df.query("abs(GenPart_pdgIdMother) == 24 or GenPart_pdgIdMother == 23")
    df = df.reset_index()

    df_counts = df.groupby("entry")["GenPart_pdgId"].agg(
        n_ele=lambda x: np.sum(np.abs(x) == 11),
        n_mu=lambda x: np.sum(np.abs(x) == 13),
        n_tau=lambda x: np.sum(np.abs(x) == 15),
    )

    return df_counts.sum(axis=1)


class Test(unittest.TestCase):
    def test_genpart_1(self):

        assert count_leptons_from_weak_boson_decays("nano_data/wwz_single_lepton_filter.root").min() == 1
        assert count_leptons_from_weak_boson_decays("nano_data/wwz_double_lepton_filter.root").min() == 2


if __name__ == "__main__":

    unittest.main(verbosity=2)
