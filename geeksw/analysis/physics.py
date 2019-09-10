def hadron_collider_mt2(p1, p2):
    """Computes the transverse mass in two-particle system.

    Parameters
    ----------
    p1 : TLorentzVector
        The first particle
    p2 : TLorentzVector
        The second particle

    Returns
    -------
    The transverse mass of the two-particle system as defined in [1].

    Notes
    -----

    * ``p1`` and ``p2`` can also be arrays

    Warning
    -------

    This is the definition of transverse mass as hadron collider physicists use it! Check Wikipedia [1] for more
    details.

    References
    ----------

    [1] https://en.wikipedia.org/wiki/Transverse_mass

    """
    return (p1.mt + p2.mt) ** 2 - (p1 + p2).pt2
