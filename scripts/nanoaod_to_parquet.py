from geeksw.nanocache import list_files
from geeksw.nanoaod import nanoaod_to_parquet


import os
import subprocess


def convert_dataset_to_parquet(dataset):

    server = "root://polgrid4.in2p3.fr/"

    input_files = list_files(dataset)

    base_out_dir = "/eos/user/r/rembserj/parquet"

    n = len(input_files)

    for i, input_file in enumerate(input_files):

        out_dir = base_out_dir + os.path.dirname(input_file)

        tmp_file_name = os.path.join("/tmp", os.path.basename(input_file))
        subprocess.call(["rm", tmp_file_name])

        print(f"File {i+1} of {n}: copying " + input_file + " to " + tmp_file_name)
        subprocess.call(["xrdcp", server + input_file, tmp_file_name])

        nanoaod_to_parquet([tmp_file_name], out_dir, entrystop=None, progressbar=False)

        subprocess.call(["rm", tmp_file_name])
        print("Deleted " + tmp_file_name)


if __name__ == "__main__":

    datasets = [
        "/WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8/RunIISummer16NanoAODv5-PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7-v1/NANOAODSIM"
    ]

    for dataset in datasets:
        convert_dataset_to_parquet(dataset)
