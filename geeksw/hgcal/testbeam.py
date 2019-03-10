import pandas as pd
import os
import io
import numpy as np
from types import MethodType
import glob
import uproot
import awkward


# data_path = "/home/llr/ilc/appro2/data/ntuples/v11"
data_path = "/data_CMS/cms/rembser/store/group/dpg_hgcal/tb_hgcal/2018/cern_h2_october/offline_analysis/ntuples/v11"


def load_run(
    run, columns=None, key="rechitntupler/hits", entrystart=None, entrystop=None, data_path=data_path, mask_noisy=True, verbosity=0
):

    if verbosity > 0:
        print("Loading " + key + " from run " + str(run) + "...", end=" ")

    if key == "rechitntupler/hits":
        colnames_from_sampling = ["rechit_dE", "rechit_X0", "rechit_Lambda"]
        colnames_in_sampling = ["dE", "X0", "Lambda"]
    else:
        colnames_from_sampling = []
        colnames_in_sampling = []

    requires_layer = False
    if not columns is None:
        for c in columns:
            if c in colnames_from_sampling and not "rechit_layer" in columns:
                columns.append("rechit_layer")

    # Load the ntuple
    file_path = os.path.join(data_path, "ntuple_{0}.root".format(run))
    branches_from_tree = None
    if not columns is None:
        branches_from_tree = [c for c in columns if not c in colnames_from_sampling]
        if mask_noisy:
            branches_from_tree += ["rechit_chip", "rechit_module", "rechit_layer"]
    df = uproot.open(file_path)[key].pandas.df(branches=branches_from_tree, entrystart=entrystart, entrystop=entrystop)

    # Add the dE/dX weights, X0 and lambda to the data frame for convenience
    if columns is None:
        a = colnames_from_sampling
        b = colnames_in_sampling
    else:
        a = []
        b = []
        for c in columns:
            if c in colnames_from_sampling:
                i = colnames_from_sampling.index(c)
                a.append(colnames_from_sampling[i])
                b.append(colnames_in_sampling[i])

    # Remove the rechits coming from the noisy chip in the  first layer
    if mask_noisy and key == "rechitntupler/hits":
        df = df.query("not(rechit_chip == 0 and rechit_module == 78 and rechit_layer == 1)").copy()

    configuration = runlist[runlist.Run == run].CaloConfiguration.values[0]

    # Add information from the sampling factors data
    if len(a) > 0:
        sampling_factors_layer_idx = sampling_factors[configuration].set_index("Layer")
        values = sampling_factors_layer_idx.loc[df.rechit_layer, b].values
        for i, ai in enumerate(a):
            df[ai] = values[:, i]

    if verbosity > 0:
        print("Done.")

    if not columns is None:
        return df[columns]

    return df


def load_run_ranges():
    file_path = os.path.join(os.path.dirname(__file__), "data/run_ranges.csv")
    return pd.read_csv(file_path, comment="#")


def iterate_runs(runlist, query=None, **kwargs):
    """Iterate over some runs fulfilling a query.
    """
    queried_runlist = runlist if query is None else runlist.query(query)
    for idx in range(len(queried_runlist)):
        yield runlist.iloc[idx], load_run(runlist.iloc[idx]["Run"], **kwargs)


def load_runlist(data_path=data_path):
    # download the runlist
    file_path = os.path.join(os.path.dirname(__file__), "data/cern_Oct2018_runlist_clean_v1.csv")
    runlist = pd.read_csv(file_path)

    # only runs from 384 onward are considered as good
    runlist = runlist.query("Run >= 384")

    # Fix the probelm with duplicate run 697 where the second one is actually run 698
    runlist = runlist.drop(runlist[runlist.Run == 698].index)
    duplicate_run_idx = runlist[runlist.Run == 697].index[1]
    runlist.at[duplicate_run_idx, "Run"] = 698

    # Fix duplicate run 116
    duplicate_run_idx = runlist[runlist.Run == 1115].index[1]
    runlist.at[duplicate_run_idx, "Run"] = 1116

    # we only care about the runs which are actually available as HDF tables
    files = glob.glob(os.path.join(data_path, "ntuple_*.root"))
    available_runs = [int(f[:-5].split("_")[-1]) for f in files]

    runlist = runlist[np.in1d(runlist.Run, available_runs)]

    runlist = runlist.sort_values("Run")

    # Only select "interesting" columns
    runlist = runlist[["Run", "date", "Nevents", "Particle", "Energy"]]
    # Consistent upper case
    runlist.columns = ["Run", "Date", "Nevents", "Particle", "Energy"]

    # Add the configuration
    runlist["Configuration"] = np.nan
    for config, start, stop in zip(
        run_ranges["Configuration"].values, run_ranges["First Run"].values, run_ranges["Last Run"].values
    ):
        runlist.loc[np.logical_and(runlist.Run >= start, runlist.Run <= stop), "Configuration"] = config

    # Make a new column which tells you which configuration the run is corresponding to the nomenclature on slide 5:
    # https://llrgit.in2p3.fr/rembser/hgc-testbeam-mini-stage/blob/master/slides/HGC_TBOct2018_Summary.pdf
    # It was found out how the Configuration relates to this other configuration between 1 and 3 using this website:
    # https://gitlab.cern.ch/cms-hgcal-tb/TestBeam/wikis/configurations/description
    runlist["CaloConfiguration"] = runlist.Configuration.apply(lambda x: int(x[1]) - 1)

    # Bind the iterate method to the runlist
    runlist.iterate = MethodType(iterate_runs, runlist)

    return runlist


def run_info(run):
    return runlist[runlist.Run == run]


def load_sampling_factors():
    sampling_factors = {}
    for i in range(1, 4):
        file_path = os.path.join(os.path.dirname(__file__), "data/samplingfactors{0}.csv".format(i))
        sampling_factors[i] = pd.read_csv(file_path, comment="#")
    return sampling_factors


sampling_factors = load_sampling_factors()
run_ranges = load_run_ranges()
runlist = load_runlist()


def get_df_layers(df, configuration, max_layer=28):
    """Get the energy sums per layer, including X0 information.
    Args:
        df (pandas.DataFrame): HGCal ntuple, which must have the following
            columns available: "event", "rechit_energy", "rechit_layer".
        configuration (int): the testbeam configuration number, either 1,
            2 or 3.
        max_layer;
        a (array_like): The array with the variable we want to reweight.
        reference (scalar or array_like): Either a scalar value if you want to
            reweight to a flat distribution, or an array for extracting the
            distribution to match.
        bins (int or sequence of scalars or str, optional) If `bins` is an int,
            it defines the number of equal-width bins in the given range (10,
            by default). If `bins` is a sequence, it defines the bin edges,
            including the rightmost edge, allowing for non-uniform bin widths.
            If `bins` is a string, it defines the method used to calculate the
            optimal bin width, as defined by `numpy.histogram_bin_edges`.
        get_w_ref (bool, optinal): If set to true, weights for the reference
            distribution will also be returned.
    Returns:
        w (array of dtype float): The weights for the input array to match the
            reference arrays distribution.
        w_ref (darray of dtype float, optional) The weights for the reference
            array, with are 1 in the binning and 0 outside.
    Notes:
        If an entry of `a` falls out of the binning range or the refrence has
        zero entries in that bin, its weight will be zero.
    Examples:
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>>
        >>> # Exponential background and Gaussian signal
        >>> bkg = np.random.exponential(scale=1.0, size=n)
        >>> sig = np.random.normal(loc=2.0, scale=1.0, size=n)
        >>>
        >>> # Calculate weights
        >>> w_sig, w_bkg = reweight1d(sig, bkg, bins=200)
        >>> # Plot histograms
        >>> bins = np.linspace(-2, 7, 200)
        >>> plt.hist(sig, bins=bins, weights=w_sig, label="sig")
        >>> plt.hist(bkg, bins=bins, weights=w_bkg, label="bkg")
        >>> plt.legent(loc="upper right")
        >>> plt.show()
    """

    df_q = df.query("rechit_layer <= 28")
    df = df[df.rechit_layer <= max_layer]
    df_layers = df.groupby(["event", "rechit_layer"])["rechit_energy"].sum()

    events = df_layers.reset_index().event.unique()
    nevents = len(events)

    repeated_events = np.repeat(events, max_layer)
    repeated_layers = np.tile(np.arange(1, max_layer+1), nevents)

    sampling_factors_layer_idx = sampling_factors[configuration].set_index("Layer")
    x0_values = sampling_factors_layer_idx.loc[repeated_layers, "X0"].values
    empty_df = pd.DataFrame(data={"rechit_X0": x0_values},
                            index=pd.MultiIndex.from_arrays([repeated_events, repeated_layers],
                                                            names=("event", "rechit_layer")))

    df_layers = pd.concat([empty_df, df_layers], axis=1)
    df_layers = df_layers.fillna(0.0)

    assert(len(df_layers) == max_layer * nevents)

    return df_layers
