import numpy as np
import awkward


def get_pdgIdMother(df):
    """Get the PDG ID of the mother particles.

    Parameters
    ----------
    df : pandas.DataFrame
        Data frame with NanoAOD GenPart info with multi-level-index.

    Returns
    -------
    numpy.ndarray
        An integer array with with PDG IDs of the mother particles.

    Examples
    --------

    >>> events = uproot.open("nano.root")["Events"]
    >>> df = events.pandas.df([b"GenPart_genPartIdxMother", b"GenPart_pdgId"])
    >>> df["GenPart_pdgIdMother"] = get_pdgIdMother(df)

    """

    pdgid = df["GenPart_pdgId"].values
    mother_idx = df["GenPart_genPartIdxMother"].values
    mother_pdgid = np.zeros_like(mother_idx)
    sub = df.index.get_level_values(1).values

    n_sub = np.concatenate([sub[:-1][np.diff(sub) != 1], [sub[-1]]]) + 1
    offset = np.cumsum(np.concatenate([[0], n_sub[:-1]]))

    offsets = (awkward.JaggedArray.fromcounts(n_sub, np.zeros(len(df), dtype=np.int)) + offset).flatten()

    mother_pdgid[mother_idx >= 0] = pdgid[(mother_idx + offsets)[mother_idx >= 0]]

    return mother_pdgid
