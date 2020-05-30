from uproot_methods import TLorentzVectorArray

from .LHEReader import LHEReader


def get_p4_array(particles):
    return TLorentzVectorArray(particles["px"], particles["py"], particles["pz"], particles["energy"])
