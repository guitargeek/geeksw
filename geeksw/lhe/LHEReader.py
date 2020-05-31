import pandas as pd
import gzip
from io import StringIO
import xml.etree.ElementTree as ET
import awkward
import numpy as np

import datetime


def print_log(*args, **kwargs):
    time_string = datetime.datetime.now()
    print(f"[{time_string}]", *args, **kwargs)


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


class NestedListIterator(object):
    def __init__(self, nested_list):
        self.iter_outer_ = iter(nested_list)
        self.iter_inner_ = iter(next(self.iter_outer_))

    def __next__(self):
        try:
            return next(self.iter_inner_)
        except StopIteration:
            self.iter_inner_ = iter(next(self.iter_outer_))
            return next(self.iter_inner_)


class NestedList(object):
    def __init__(self, nested_list):
        self.nested_list_ = nested_list

    def __iter__(self):
        return NestedListIterator(self.nested_list_)


def read_lhe_file(file_handle, batch_size=1000, maxevents=None):

    header_read = False
    data_header = []

    data = [b"<LesHouchesEvents>"]
    do_batching = not batch_size is None and batch_size > 0
    batch_starts = [1]
    i_event = 0

    print_log("looping over lines in file")

    for line in file_handle:

        if not header_read:
            # Read the part of the XML that doesn't belong to the list of events
            if b"<event>" in line:
                header_read = True
                data_header.append(b"</LesHouchesEvents>")
                data.append(line)
            else:
                data_header.append(line)
            continue

        if not maxevents is None and i_event == maxevents:
            data.append(b"</LesHouchesEvents>")
            break
        data.append(line)
        if b"</event>" in line:
            if i_event % 1000 == 0:
                print_log("Reading event:", i_event + 1)
            if do_batching and (i_event + 1) % batch_size == 0:
                batch_starts.append(len(data))
            i_event += 1

    print_log("reading header XML from binary string")
    joined_data_header = b"".join(data_header)
    root_header = ET.fromstring(joined_data_header)

    if not do_batching:
        print_log("joining binary data")
        joined_data = b"".join(data)

        print_log("reading events XML from binary string")
        root_events = ET.fromstring(joined_data)
    else:
        print_log("reading events XML by batches")
        root_events_list = []
        for a, b in zip(batch_starts[:-1], batch_starts[1:]):
            print_log(f"...parsing batch {len(root_events_list) + 1}")
            joined_data = b"".join([b"<LesHouchesEvents>"] + data[a:b] + [b"</LesHouchesEvents>"])
            root_events_list.append(ET.fromstring(joined_data))

        root_events = NestedList(root_events_list)

    return root_header, root_events


class LHEReader(object):
    def __init__(self, lhe_filepath, maxevents=None, batch_size=100):

        print_log(f"opening LHE file {lhe_filepath}")

        if lhe_filepath.endswith(".lhe.gz"):
            with gzip.open(lhe_filepath, "r") as f:
                _, self.root_ = read_lhe_file(f, maxevents=maxevents, batch_size=batch_size)
        elif lhe_filepath.endswith(".lhe"):
            with open(lhe_filepath, "r") as f:
                _, self.root_ = read_lhe_file(f, maxevents=maxevents, batch_size=batch_size)
        else:
            raise RuntimeError(f"File {lhe_filepath} not recognized as LHE file. It should end with .lhe or .lhz.gz")

        print_log("reading file into XML data structures done")

    def event_data_frame(self):
        return get_event_data_frame(self.root_)

    def particle_data_frame(self):
        return get_particle_data_frame(self.root_)

    def reweighting_data_frame(self):
        return get_reweighting_data_frame(self.root_)
