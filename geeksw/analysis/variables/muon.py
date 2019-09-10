import numpy as np


def triboson_us_selection(df, working_point, pt_threshold=10.0):
    # from https://indico.cern.ch/event/769246/contributions/3494885/attachments/1877118/3091417/PhilipChang20190709_SMPVV_WVZ4or5Lep_MBA.pdf
    working_points = ["veto", "nominal"]

    if not working_point in working_points:
        raise ValueError('working_point has to be any of "' + '", "'.join(working_points) + '".')

    is_ee = df["Muon_eta"] >= 1.497

    dz_cut = 0.1 + is_ee * 0.1  # 0.1 in EB, 0.2 in EE
    pass_dz = df["Muon_dz"].abs() < dz_cut

    dxy_cut = 0.05 + is_ee * 0.05  # 0.05 in EB, 0.1 in EE
    pass_dxy = df["Muon_dxy"].abs() < dxy_cut

    pass_sip3d = df["Muon_sip3d"].abs() < 4.0

    iso_cut = 0.25 if working_point == "veto" else 0.15
    pass_isolation = df["Muon_pfRelIso04_all"] < iso_cut

    return df[
        np.logical_and.reduce(
            [
                df["Muon_mediumId"],
                df["Muon_pt"] >= pt_threshold,
                df["Muon_eta"].abs() < 2.4,
                pass_dz,
                pass_dxy,
                pass_isolation,
                pass_sip3d,
            ]
        )
    ]
