import numpy as np


def pass_cut_based_id(df, working_point):
    """Checks which electrons pass a given cut-based working point.

    Parameters
    ----------
    df : pandas.DataFrame
        A data frame with electron data.
    working_point: str
        The name of the working point, i.e. ``veto``, ``loose``, ``medium`` or ``tight``.

    Returns
    -------
    pandas.Series
        The ID decisions for each electron.

    Notes
    -----

    * Check the NanoAOD documentation for the ``Electron_cutBased`` branch (here for the latest 102X campaign [1]) to know which ID is used

    References
    ----------

    [1] https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html#Electron

    """
    working_points = ["veto", "loose", "medium", "tight"]

    if not working_point in working_points:
        raise ValueError('working_point has to be any of "' + '", "'.join(working_points) + '".')

    return df["Electron_cutBased"] > working_points.index(working_point)


def supercluster_eta(df):
    """Calculates :math:`\eta` of the superclusters corresponding to the electrons.

    Parameters
    ----------
    df : pandas.DataFrame
        A data frame with electron data.

    Returns
    -------
    pandas.Series
        The locations of the superclusters in :math:`eta` for each electron.

    Notes
    -----

    * NanoAOD stores only the difference between the supercluster eta and the electron :math:`eta` [1], hence the supercluster eta has to be reconstructed by subtracting the electron :math:`\eta` from that difference
    * It's not clear to me what is stored as the supercluser :math:`\eta` in case there was no supercluster (tracker-driven electron)
    * This function was written for NanoAOD produced with 102X in the ``Nano14Dec2018`` campaign [2]

    References
    ----------

    [1] https://github.com/cms-sw/cmssw/blob/CMSSW_10_2_X/PhysicsTools/NanoAOD/python/electrons_cff.py#L320

    [2] https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html#Electron

    """
    return df["Electron_deltaEtaSC"] + df["Electron_eta"]


def is_endcap(df):
    """Checks which electrons were measured in the ECAL endcaps.

    Parameters
    ----------
    df : pandas.DataFrame
        A data frame with electron data.

    Returns
    -------
    pandas.Series
        If each electrons supercluster was measured in the ECAL endcap or not.

    Notes
    -----

    * It is checked if the supercluster :math:`|\eta| >= 1.479`, a value also used within the EGM POG [1].

    References
    ----------

    [1] https://github.com/cms-sw/cmssw/blob/CMSSW_10_2_X/RecoEgamma/ElectronIdentification/python/Identification/cutBasedElectronID_tools.py#L5

    """
    return np.abs(supercluster_eta(df)) > 1.479


def very_loose_id(df):

    # adapted from wvzBabyMaker::isPt10VeryLooserThanPOGVetoElectron(int idx)

    is_ee = is_endcap(df)

    return df[
        np.logical_and.reduce(
            [
                df["Electron_pt"] > 10.0,
                pass_cut_based_id(df, "veto"),
                df["Electron_eta"].abs() < 2.5,
                df["Electron_dz"].abs() < 0.1 + is_ee * 0.1,
                df["Electron_dxy"].abs() < 0.05 + is_ee * 0.05,
            ]
        )
    ]
