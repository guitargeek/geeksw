import numpy as np


def zpairs(particles, z_mass=91.19, return_by_charge=False):
    """Returns the two indices per event that form a pair closest to the Z mass.

    Args:
        particles (uproot_methods.TLorentzVectorArray): a jagged array holding
            the particles. If the underlying table also holds the attributes
            "flavour" or "charge", this method will consider this to only
            consider pairs of the same flavour and opposite charge.
        z_mass (float, optional): the mass of the Z boson.
        return_by_charge (bool, optional): if set, this method will return the
            indecies for the negatively charged and positively charged particles
            in the pair separately.

    Returns:
        a single or tuple of awkward.array.jagged.JaggedArray: the indices to
        select the particles making up the best Z pair cadidate per event.
    """
    combinations = particles.cross(particles, nested=True)

    pair_masses = (combinations.i0 + combinations.i1).mass

    pair_masses.content.content = np.nan_to_num(pair_masses.content.content)

    if "charge" in particles.columns:
        charge = particles["charge"]
        charge_combinations = charge.cross(charge, nested=True)
        pair_charges = charge_combinations.i0 + charge_combinations.i1
        pair_masses.content.content *= pair_charges.content.content == 0

    if "flavour" in particles.columns:
        flavour = particles["flavour"]
        flavour_combinations = flavour.cross(flavour, nested=True)
        pair_flavours = flavour_combinations.i0 - flavour_combinations.i1
        pair_masses.content.content *= pair_flavours.content.content == 0

    z_residues = np.abs(pair_masses - z_mass)

    best_residues = z_residues.min().min()

    is_in_best_pair = (z_residues == best_residues).any()

    is_in_best_pair = np.logical_and(is_in_best_pair, is_in_best_pair.counts >= 2)

    is_positive_in_best_pair = np.logical_and(charge > 0, is_in_best_pair)
    is_negative_in_best_pair = np.logical_and(charge <= 0, is_in_best_pair)

    positive_idx = is_positive_in_best_pair.argmax()
    negative_idx = is_negative_in_best_pair.argmax()

    valid = positive_idx != negative_idx

    positive_idx = positive_idx[valid]
    negative_idx = negative_idx[valid]

    if return_by_charge:
        return negative_idx, positive_idx

    return negative_idx.concatenate([positive_idx], axis=1)


def match(particles, others, delta_r=0.4):
    eta_combs = particles.eta.cross(others.eta, nested=True)
    phi_combs = particles.phi.cross(others.phi, nested=True)

    return ((phi_combs.i1 - phi_combs.i0) ** 2 + (eta_combs.i1 - eta_combs.i0) ** 2 < delta_r ** 2).any()


def crossclean(particles, others, delta_r=0.4):

    import pandas
    from ..analysis import cmspandas
    from ..analysis import utils

    if not isinstance(particles, pandas.DataFrame):
        return particles[~match(particles, others, delta_r=delta_r)]

    df1, df2 = particles, others

    name1 = df1.columns[0].split("_")[0]
    name2 = df2.columns[0].split("_")[0]

    e1 = cmspandas.unique_events(df1)
    e2 = cmspandas.unique_events(df2)

    m1 = ~((cmspandas.array(df1[name1 + "_pt"]) < 0) + np.in1d(e1, e2)).flatten()
    m2 = ~((cmspandas.array(df2[name2 + "_pt"]) < 0) + np.in1d(e2, e1)).flatten()

    p1 = utils.lorentz_vector_array(df1[~m1])
    p2 = utils.lorentz_vector_array(df2[~m2])

    m1[~m1] = ~(match(p1, p2, delta_r=delta_r)).flatten()

    return df1[m1]
