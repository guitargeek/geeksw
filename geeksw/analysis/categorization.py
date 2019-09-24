from . import variables
from . import cmspandas
from . import utils

import pandas
import numpy


def foo(data):

    df_ele = variables.leptons.triboson_us_selection(data["Electron"], "veto", pt_threshold=10.0)
    df_muon = variables.leptons.triboson_us_selection(data["Muon"], "veto", pt_threshold=10.0)
    df_scalar = data["Scalar"]
    df_jet = data["Jet"]

    df_ele["Electron_PuppiMT"] = variables.leptons.transverse_mass_with_met(df_ele, df_scalar)
    df_muon["Muon_PuppiMT"] = variables.leptons.transverse_mass_with_met(df_muon, df_scalar)

    def triboson_us_pair_selection(df_ele, df_muon):

        # get all pairs
        df_ele_pairs = variables.leptons.invariant_mass_pairs(df_ele)
        df_muon_pairs = variables.leptons.invariant_mass_pairs(df_muon)

        # require that one electron has at least a pT of 25 GeV
        df_ele_pairs = df_ele_pairs[df_ele_pairs[["Electron_pt", "AntiElectron_pt"]].max(axis=1) >= 25.0]
        df_muon_pairs = df_muon_pairs[df_muon_pairs[["Muon_pt", "Muon_pt"]].max(axis=1) >= 25.0]

        # now select the pairs closest to the Z mass for each electrons and muons
        df_ele_pairs = variables.leptons.best_z_boson_pairs(df_ele_pairs)
        df_muon_pairs = variables.leptons.best_z_boson_pairs(df_muon_pairs)

        # and cross-clean them so there is only one (the best) Z boson pair candidate per event
        return variables.leptons.crossclean_pairs(df_ele_pairs, df_muon_pairs)

    df_ele_pairs, df_muon_pairs = triboson_us_pair_selection(df_ele, df_muon)

    def remaining_nominal_leptons(df_lepton, df_lepton_pairs):
        particle = df_lepton.columns[0].split("_")[0]

        df_remaining = cmspandas.unselect_objects(df_lepton, df_lepton_pairs[particle])
        df_remaining = cmspandas.unselect_objects(df_remaining, df_lepton_pairs["Anti" + particle])
        return variables.leptons.triboson_us_selection(df_remaining, "nominal")

    def count_leptons_over_mt(df_lep, threshold=20.0):
        particle = df_lep.columns[0].split("_")[0]
        index = cmspandas.unique_events(df_lep)
        v = utils.to_jagged(df_lep[particle + "_PuppiMT"] > threshold).sum()
        s = pandas.Series(v, index=index)
        s.index.name = "event"
        return s

    df_W_ele = remaining_nominal_leptons(df_ele, df_ele_pairs)
    df_W_muon = remaining_nominal_leptons(df_muon, df_muon_pairs)

    df_W_ele_pairs, df_W_muon_pairs = triboson_us_pair_selection(df_W_ele, df_W_muon)

    df_analysis = pandas.DataFrame(index=df_scalar.index)

    df_analysis["nBjets"] = 0
    df_analysis.loc[df_ele_pairs.index, "Z_candidate"] = df_ele_pairs["Electron_pair_mass"]
    df_analysis.loc[df_muon_pairs.index, "Z_candidate"] = df_muon_pairs["Muon_pair_mass"]
    df_analysis.loc[df_W_ele_pairs.index, "second_Z_candidate"] = df_W_ele_pairs["Electron_pair_mass"]
    df_analysis.loc[df_W_muon_pairs.index, "second_Z_candidate"] = df_W_muon_pairs["Muon_pair_mass"]

    n_bjets = variables.jet.n_bjets(df_jet, "DeepCSV", "loose", pt_threshold=20.0)

    df_analysis.loc[n_bjets.index, "nBjets"] = n_bjets

    df_analysis = cmspandas.add_column(df_analysis, utils.count(df_W_ele), "n_W_electron", default_value=0)
    df_analysis = cmspandas.add_column(df_analysis, utils.count(df_W_muon), "n_W_muon", default_value=0)

    index = cmspandas.unique_events(df_W_ele)
    v = utils.to_jagged(df_W_ele["Electron_charge"]).sum()
    s = pandas.Series(v, index=index)
    s.index.name = "event"
    df_analysis = cmspandas.add_column(df_analysis, s, "W_Electron_charge_sum", 0)

    index = cmspandas.unique_events(df_W_muon)
    v = utils.to_jagged(df_W_muon["Muon_charge"]).sum()
    s = pandas.Series(v, index=index)
    s.index.name = "event"
    df_analysis = cmspandas.add_column(df_analysis, s, "W_Muon_charge_sum", 0)

    index = cmspandas.unique_events(df_W_ele)
    v = utils.to_jagged(df_W_ele["Electron_pt"] > 25).sum()
    s = pandas.Series(v, index=index)
    s.index.name = "event"
    df_analysis = cmspandas.add_column(df_analysis, s, "W_Electron_pass_pt", 0)

    index = cmspandas.unique_events(df_W_muon)
    v = utils.to_jagged(df_W_muon["Muon_pt"] > 25).sum()
    s = pandas.Series(v, index=index)
    s.index.name = "event"
    df_analysis = cmspandas.add_column(df_analysis, s, "W_Muon_pass_pt", 0)

    df_analysis["W_Leptons_charge_sum"] = df_analysis["W_Electron_charge_sum"] + df_analysis["W_Muon_charge_sum"]
    df_analysis["W_Leptons_pass_pt"] = df_analysis["W_Electron_pass_pt"] + df_analysis["W_Muon_pass_pt"]

    df_analysis["W_Leptons_over_Mt_20"] = count_leptons_over_mt(df_W_ele, 20.0) + count_leptons_over_mt(df_W_muon, 40.0)
    df_analysis["W_Leptons_over_Mt_40"] = count_leptons_over_mt(df_W_ele, 40.0) + count_leptons_over_mt(df_W_muon, 40.0)
    df_analysis["W_Leptons_over_Mt_20"] = df_analysis["W_Leptons_over_Mt_20"].fillna(0).astype(int)
    df_analysis["W_Leptons_over_Mt_40"] = df_analysis["W_Leptons_over_Mt_40"].fillna(0).astype(int)

    df_analysis = df_analysis.drop(["W_Electron_charge_sum", "W_Muon_charge_sum"], axis=1)
    df_analysis = df_analysis.drop(["W_Electron_pass_pt", "W_Muon_pass_pt"], axis=1)

    df_analysis["MET"] = df_scalar["PuppiMET_pt"]

    n = len(df_analysis)

    df_analysis = df_analysis.query("abs(Z_candidate - 91.19) <= 10.0 and n_W_electron + n_W_muon == 2")
    df_analysis = df_analysis.query("W_Leptons_charge_sum == 0")
    df_analysis = df_analysis.query("W_Leptons_pass_pt >= 1")

    def is_e_mu_SR(df):
        return numpy.logical_and.reduce(
            [
                df["n_W_electron"] == 1,
                df["nBjets"] == 0,
                df["W_Leptons_over_Mt_40"] >= 1,
                df["W_Leptons_over_Mt_20"] == 2,
            ]
        )

    def is_btag_CR(df):
        return numpy.logical_and.reduce([df["n_W_electron"] == 1, df["nBjets"] > 0])

    def is_on_Z_CR(df):
        return numpy.logical_and.reduce(
            [
                numpy.abs(df["n_W_electron"] - df["n_W_muon"]) == 2,
                df["nBjets"] == 0,
                numpy.abs(df["second_Z_candidate"] - 91.19) <= 10.0,
            ]
        )

    def is_off_Z_SR(df):
        return numpy.logical_and.reduce(
            [
                df["n_W_electron"] + df["n_W_muon"] == 2,
                numpy.abs(df["n_W_electron"] - df["n_W_muon"]) == 2,
                df["nBjets"] == 0,
                ~(numpy.abs(df["second_Z_candidate"] - 91.19) <= 10.0),
                df["MET"] >= 100.0,
            ]
        )

    return pandas.DataFrame(
        {
            "e_mu_SR": [numpy.sum(is_e_mu_SR(df_analysis))],
            "b_tag_CR": [numpy.sum(is_btag_CR(df_analysis))],
            "on_Z_CR": [numpy.sum(is_on_Z_CR(df_analysis))],
            "off_Z_SR": [numpy.sum(is_off_Z_SR(df_analysis))],
        }
    )
