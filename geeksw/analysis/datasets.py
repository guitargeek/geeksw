import geeksw.nanoaod.parquet
from geeksw.utils.filesystem import descend

import os

cross_section = {
    "WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8": 0.1651,
    "WWZ_TuneCP5_13TeV-amcatnlo-pythia8": 0.1651,
    "WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8": 0.1651,
    "VHToNonbb_M125_13TeV_amcatnloFXFX_madspin_pythia8": 0.952,
    "ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1": 3.6818,
}

luminosity = {
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable
    2016: 35.92,
    2017: 41.53,
    2018: 59.74,
}

campaign = {
    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmVAnalysisSummaryTable
    2016: "RunIISummer16NanoAODv5",
    2017: "RunIIFall17NanoAODv5",
    2018: "RunIIAutumn18NanoAODv5",
}


def open_dataset(dataset, year, data_dir="~/data/parquet"):
    data_dir = os.path.join(data_dir, "store/mc", campaign[year], dataset)
    data_dir = os.path.expanduser(descend(data_dir))
    data = geeksw.nanoaod.parquet.open(data_dir)

    return data
