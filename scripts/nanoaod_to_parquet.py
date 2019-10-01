from geeksw.nanoaod import convert_dataset_to_parquet


if __name__ == "__main__":

    datasets = [
        "/WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM"
    ]

    base_out_dir = "/eos/user/r/rembserj/parquet"

    for dataset in datasets:
        convert_dataset_to_parquet(dataset, base_out_dir)
