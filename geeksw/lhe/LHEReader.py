import pandas as pd
import gzip
from io import StringIO
import xml.etree.ElementTree as ET
import awkward
import numpy as np


def reduce_duplicate_whitespace(text):
    text = text.replace("  ", " ")
    if "  " in text:
        return reduce_duplicate_whitespace(text)
    return text


def get_event_data_frame(root):
    first_event_lines = []

    for child in root:
        if child.tag == "event":
            text = reduce_duplicate_whitespace(child.text)
            first_line = text.strip().split("\n")[0].strip()
            first_event_lines.append(first_line)

    first_event_line_header = " ".join(list([str(x) for x in range(6)]))
    text = first_event_line_header + "\n" + "\n".join(first_event_lines)
    return pd.read_csv(StringIO(text), sep=" ", index_col=False)


def get_particle_data_frame(root):
    particle_table_lines = []

    for child in root:
        if child.tag == "event":
            text = reduce_duplicate_whitespace(child.text)
            lines = text.strip().split("\n")
            text = [l.strip() for l in lines[1:]]
            particle_table_lines.append(text)

    event_table_header = " ".join(list([str(x) for x in range(13)]))
    event_table_header = [
        "pdgid",
        "status",
        "mother1",
        "mother2",
        "color1",
        "color2",
        "px",
        "py",
        "pz",
        "energy",
        "mass",
        "lifetime",
        "spin",
    ]

    text = " ".join(event_table_header) + "\n" + "\n".join(["\n".join(lines) for lines in particle_table_lines])
    df = pd.read_csv(StringIO(text), sep=" ", index_col=False)

    # add the event number
    particle_counts = np.array([len(lines) for lines in particle_table_lines])
    event = awkward.JaggedArray.fromcounts(particle_counts, np.zeros(np.sum(particle_counts), dtype=np.int))
    event = event + np.arange(len(particle_counts))
    event = event.flatten()
    columns = list(df.columns)
    df["event"] = event
    df = df[["event"] + columns]

    return df


def get_reweighting_data_frame(root):
    weight_ids = []
    weights = []

    for event in root:
        if event.tag == "event":
            for rwgt in event:
                if rwgt.tag == "rwgt":
                    if weight_ids == []:
                        for wgt in rwgt:
                            weight_ids.append(wgt.attrib["id"])
                    for wgt in rwgt:
                        weights.append(float(wgt.text))

    weights = np.array(weights)
    n_weights = len(weight_ids)
    return pd.DataFrame(weights.reshape((-1, n_weights)), columns=weight_ids)


class LHEReader(object):
    def __init__(self, lhe_filepath):
        if lhe_filepath.endswith(".lhe.gz"):
            with gzip.open(lhe_filepath, "r") as f:
                self.root_ = ET.fromstring(f.read())
        elif lhe_filepath.endswith(".lhe"):
            with open(lhe_filepath, "r") as f:
                self.root_ = ET.fromstring(f.read())
        else:
            raise RuntimeError(f"File {lhe_filepath} not recognized as LHE file. It should end with .lhe or .lhz.gz")

    def event_data_frame(self):
        return get_event_data_frame(self.root_)

    def particle_data_frame(self):
        return get_particle_data_frame(self.root_)

    def reweighting_data_frame(self):
        return get_reweighting_data_frame(self.root_)
