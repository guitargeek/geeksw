from geeksw.nanoaod import convert_dataset_to_parquet


if __name__ == "__main__":

    datasets = [
        # "/WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8/RunIIFall17NanoAODv5-PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/NANOAODSIM",
        "/WWZ_TuneCP5_13TeV-amcatnlo-pythia8/RunIIAutumn18NanoAODv5-Nano1June2019_102X_upgrade2018_realistic_v19_ext1-v1/NANOAODSIM"
    ]

    # base_out_dir = "/eos/user/r/rembserj/parquet"
    base_out_dir = "/data_CMS/cms/rembser/parquet"

    for dataset in datasets:
        convert_dataset_to_parquet(dataset, base_out_dir)
