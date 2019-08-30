import uproot
import os
import pandas as pd
import numpy as np
import awkward
from tqdm import tqdm

vector_groups = [
    "Electron",
    "Jet",
    "Tau",
    "Photon",
    "Muon",
    "IsoTrack",
    "GenVisTau",
    "SV",
    "GenJet",
    "GenJetAK8",
    "OtherPV",
    "SubJet",
    "TrigObj",
    "SoftActivityJet",
    "LHEPart",
    "FatJet",
    "GenPart",
    "SubGenJetAK8",
    "GenDressedLepton",
]

lhe_branches = ["LHEPdfWeight", "LHEScaleWeight"]


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
        
        vector_groups_present = list(filter(lambda x : "n" + x in branches, vector_groups))

        scalar_branches = ["n" + s for s in vector_groups_present]

        for br in branches:
            if br == "event":
                continue

            if br in lhe_branches:
                continue

            veto = False
            for s in vector_groups_present:
                if br.startswith(s + "_"):
                    veto = True
                    break

            if veto:
                continue

            scalar_branches.append(br)

        basename = os.path.basename(input_file)[:-5]

        log("Loading DataFrame for scalar branches")
        df_scalar = extract_scalar_data(events, scalar_branches, entrystop=entrystop, progressbar=progressbar)
        log("Saving DataFrame parquet Scalar")
        save_parquet(df_scalar, basename + "_Scalar")
        del df_scalar

        for group in vector_groups_present:
            log("Loading DataFrame for object group " + group)
            filtered_branches = list(filter(lambda br: br.startswith(group + "_"), branches))
            df = extract_vector_data(events, filtered_branches, entrystop=entrystop, progressbar=progressbar)
            log("Saving DataFrame parquet " + group)
            save_parquet(df, basename + "_" + group)
            del df

        for b in lhe_branches:
            log("Loading DataFrame for " + b + " branches")
            df = extract_vector_data(events, [b], entrystop=entrystop, progressbar=progressbar)
            log("Saving DataFrame parquet " + b)
            save_parquet(df, basename + "_" + b)
            del df
