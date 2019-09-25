import numpy
import pandas
import awkward
import uproot_methods

from .. import utils
from .. import physics
from .. import cmspandas

from . import electron
from . import muon


def invariant_mass_pairs(df):
    """Find the best Z boson pair candidates among leptons.

    Parameters
    ----------
    df : pandas.DataFrame
        A data frame with lepton data (electrons, muons or taus).

    Returns
    -------
    pandas.DataFrame
        A pandas DataFrame which tells you for each event with at least one Z boson pair candidate the indices of the
        leptons that form the best Z boson pair and their invariant mass.

    Notes
    -----

    The implementation was inspired by the jet cleaning example in awkward_array [1].

    References
    ----------

    [1] https://github.com/scikit-hep/awkward-array/blob/master/tests/test_physics.py#L18

    """

    fromcounts = awkward.JaggedArray.fromcounts

    particle = df.columns[0].split("_")[0]

    particle_mask = df[particle + "_charge"] == -1

    df_particles = df[particle_mask]
    df_anti_particles = df[~particle_mask]

    event = df.index.get_level_values(0)
    counts = utils.count(event)

    jagged_arr = fromcounts(counts, particle_mask)
    jagged_event = fromcounts(counts, event)

    particle_counts = jagged_arr.sum()
    anti_particle_counts = counts - particle_counts

    particles = utils.lorentz_vector_array(df_particles, counts=particle_counts)
    anti_particles = utils.lorentz_vector_array(df_anti_particles, counts=anti_particle_counts)

    combinations = particles.cross(anti_particles, nested=False)
    pair_masses = (combinations.i0 + combinations.i1).mass

    pair_indices = fromcounts(
        pair_masses.counts,
        utils.indices_in_event(
            (numpy.arange(len(pair_masses)) + utils.jagged_zeros(pair_masses.counts, dtype=numpy.int)).flatten()
        ),
    )

    # get the indices for the particles and antiparticles forming the pair in the LorentzVectorArrays
    particle_idx = pair_indices // anti_particle_counts
    antiparticle_idx = pair_indices % anti_particle_counts

    # get the indices for the particles and antiparticles forming the pair in the LorentzVectorArrays
    jagged_particle_idx = fromcounts(particle_counts, df_particles.index.get_level_values(1))
    jagged_antiparticle_idx = fromcounts(anti_particle_counts, df_anti_particles.index.get_level_values(1))

    jagged_particle_pt = fromcounts(particle_counts, df_particles[particle + "_pt"])
    jagged_antiparticle_pt = fromcounts(anti_particle_counts, df_anti_particles[particle + "_pt"])

    data = {
        "event": (jagged_event[:, 0] + utils.jagged_zeros(pair_masses.counts, dtype=numpy.int)).flatten(),
        "pair": pair_indices.flatten(),
        particle: jagged_particle_idx[particle_idx].flatten(),
        "Anti" + particle: jagged_antiparticle_idx[antiparticle_idx].flatten(),
        particle + "_pt": jagged_particle_pt[particle_idx].flatten(),
        "Anti" + particle + "_pt": jagged_antiparticle_pt[antiparticle_idx].flatten(),
        particle + "_pair_mass": pair_masses.flatten(),
    }

    df_pairs = pandas.DataFrame(data).set_index(["event", "pair"])

    return df_pairs


def best_z_boson_pairs(df_pairs, z_boson_mass=91.19):
    """Select only the pairs with the mass closest to the Z boson mass.

    Parameters
    ----------
    df_pairs : pandas.DataFrame
        A data frame with lepton pairs, as returned from ``invariant_mass_pairs``
    z_boson_mass : float
        The nominal mass of the Z bososn (default value is 91.19 GeV)

    Returns
    -------
    pandas.DataFrame
        A data frame with only the information about the best Z boson candidate in the event among the lepton type.

    See also
    --------

    invariant_mass_pairs : Get all pair candidates among leptons.

    """
    particle = df_pairs.columns[0].split("_")[0]

    pair_mass = cmspandas.array(df_pairs[particle + "_pair_mass"])

    min_pair_idx = (pair_mass - z_boson_mass).argmin()

    is_best_pair = utils.jagged_zeros_like(pair_mass, dtype=numpy.bool)
    is_best_pair[min_pair_idx] = True

    return df_pairs[is_best_pair.flatten()].reset_index().drop("pair", axis=1).set_index("event")


def crossclean_pairs(df_electron_pairs, df_muon_pairs, z_boson_mass=91.19):
    """Cross-clean the best Z boson candidate pairs from electrons and muons.

    Parameters
    ----------
    df_electron_pairs : pandas.DataFrame
        A data frame with electron pairs,  with at most one pair per event
    df_muon_pairs : pandas.DataFrame
        A data frame with muon pairs, with at most one pair per event
    z_boson_mass : float
        The nominal mass of the Z bososn (default value is 91.19 GeV)

    Returns
    -------
    tuple of pandas.DataFrame
        Returns again two data frames for electron and muon Z boson candidates respectively, only that pairs of one
        lepton type in events where there was also a pair of the other lepton type with a mass closer to :math:`m_Z`
        are removed.

    See also
    --------

    invariant_mass_pairs : Get all pair candidates among leptons.
    best_z_boson_pairs : Find the best Z boson pair candidates among pair candidates.

    """

    def check_unique_events(df):
        event = df.index.get_level_values("event")
        return (event[1:] != event[:-1]).all()

    if not check_unique_events(df_electron_pairs):
        raise ValueError("The electron pairs dataframe should not contain more than one pair per event!")
    if not check_unique_events(df_muon_pairs):
        raise ValueError("The muon pairs dataframe should not contain more than one pair per event!")

    df = pandas.concat([df_electron_pairs, df_muon_pairs], axis=1, join="inner")

    mask_muon = numpy.abs(df["Electron_pair_mass"] - z_boson_mass) > numpy.abs(df["Muon_pair_mass"] - z_boson_mass)
    mask_ele = numpy.abs(df["Electron_pair_mass"] - z_boson_mass) <= numpy.abs(df["Muon_pair_mass"] - z_boson_mass)

    df.loc[mask_muon, "Muon"] = numpy.nan
    df.loc[mask_ele, "Electron"] = numpy.nan

    return df_electron_pairs.drop(df["Electron"].dropna().index), df_muon_pairs.drop(df["Muon"].dropna().index)


def triboson_us_selection(df, working_point, pt_threshold=10.0):
    particle = df.columns[0].split("_")[0]

    if particle == "Electron":
        return electron.triboson_us_selection(df, working_point, pt_threshold)
    if particle == "Muon":
        return muon.triboson_us_selection(df, working_point, pt_threshold)

    raise ValueError("Can only select from electron or muon DataFrame.")


def transverse_mass_with_met(df_lepton, df_scalar, met="PuppiMET"):

    df_scalar_selected = df_scalar.loc[cmspandas.unique_events(df_lepton)]

    leptons = utils.lorentz_vector_array(df_lepton)

    met = uproot_methods.TLorentzVectorArray.from_ptetaphim(
        df_scalar_selected[met + "_pt"], 0.0, df_scalar_selected[met + "_phi"], 0
    )

    v = numpy.sqrt(physics.hadron_collider_mt2(leptons, met).flatten())
    return pandas.Series(v, index=df_lepton.index)
