import uproot
import os
import pandas as pd
import numpy as np
import awkward
from tqdm import tqdm


def extract_scalar_data(events, branches, entrystop=None, progressbar=False):
    data = {}

    data["event"] = events.array("event", entrystop=entrystop)

    for br in tqdm(branches, disable=not progressbar):
        data[br] = events.array(br, entrystop=entrystop).flatten()

    return pd.DataFrame(data)


def extract_vector_data(events, branches, entrystop=10, progressbar=False):
    def get(branch, flat=True):
        a = events.array(branch, entrystop=entrystop)
        if flat:
            return a.flatten()
        else:
            return a

    if len(branches) == 0:
        return {}

    first_branch_jagged = get(branches[0], flat=False)
    first_branch_flat = first_branch_jagged.flatten()

    event_jagged = get("event") + awkward.JaggedArray(
        first_branch_jagged.starts, first_branch_jagged.stops, np.zeros(len(first_branch_flat), dtype=np.int)
    )

    data = {}

    data["event"] = event_jagged.flatten()

    data[branches[0]] = first_branch_flat

    for br in tqdm(branches, disable=not progressbar):
        if br == branches[0]:
            continue

        if br in events:
            data[br] = get(br)
        else:
            print('Warning! Branch "' + br + '" not found in input file and skipped.')

    return pd.DataFrame(data)


def nanoaod_to_parquet(input_files, out_dir, entrystop=None, input_prefix="", progressbar=False):
    def save_parquet(df, name):
        df.to_parquet(os.path.join(out_dir, name + ".parquet.gzip"), compression="gzip", index=False)

    out_dir = os.path.expanduser(out_dir)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    n_input_files = len(input_files)

    for i, input_file in enumerate(input_files):

        log_prefix = ""
        if i > 0:
            log_prefix = f"[{i+1}/{n_input_files}] "

        def log(s):
            print(log_prefix + s)

        log("Opening input file " + input_file)
        root_file = uproot.open(input_prefix + input_file)

        events = root_file["Events"]

        branches = [br.decode("ascii") for br in events.keys()]

        n_events = len(events[branches[0]])

        prefixes = list(set([b.split("_")[0] for b in branches]))

        vector_groups_present = [p for p in prefixes if "n" + p in events]

        scalar_branches = ["n" + s for s in vector_groups_present]

        for br in branches:
            if br == "event":
                continue
            if not br.split("_")[0] in vector_groups_present:
                scalar_branches.append(br)

        basename = os.path.basename(input_file)[:-5]

        log("Loading DataFrame for scalar branches")
        df_scalar = extract_scalar_data(events, scalar_branches, entrystop=entrystop, progressbar=progressbar)
        log("Saving DataFrame parquet Scalar")
        save_parquet(df_scalar, basename + "_Scalar")
        del df_scalar

        processed_branches = scalar_branches + ["event"]

        for group in vector_groups_present:
            log("Loading DataFrame for object group " + group)
            filtered_branches = list(filter(lambda br: br == group or br.startswith(group + "_"), branches))
            df = extract_vector_data(events, filtered_branches, entrystop=entrystop, progressbar=progressbar)
            log("Saving DataFrame parquet " + group)
            save_parquet(df, basename + "_" + group)
            processed_branches += filtered_branches
            del df

        # make sure we considered all the branches
        assert [b for b in branches if not b in processed_branches] == []


from geeksw.nanocache import list_files

import os
import subprocess

def convert_files_to_parquet(input_files, base_out_dir=".", server="root://polgrid4.in2p3.fr/"):

    n = len(input_files)

    for i, input_file in enumerate(input_files):

        out_dir = base_out_dir + os.path.dirname(input_file)

        tmp_file_name = os.path.join("/tmp", os.path.basename(input_file))

        if os.path.exists(tmp_file_name):
            subprocess.call(["rm", tmp_file_name])

        print(f"File {i+1} of {n}: copying " + input_file + " to " + tmp_file_name)
        subprocess.call(["xrdcp", server + input_file, tmp_file_name])

        nanoaod_to_parquet([tmp_file_name], out_dir, entrystop=None, progressbar=False)

        subprocess.call(["rm", tmp_file_name])
        print("Deleted " + tmp_file_name)

def convert_dataset_to_parquet(dataset, base_out_dir=".", server="root://polgrid4.in2p3.fr/"):

    input_files = list_files(dataset)

    convert_files_to_parquet(input_files, base_out_dir=base_out_dir, server=server)
