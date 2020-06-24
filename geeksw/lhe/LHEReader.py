import pandas as pd
import gzip
from io import StringIO
import xml.etree.ElementTree as ET
import awkward
import numpy as np
import tqdm

import datetime

enable_debug_logging = False


def print_log(*args, **kwargs):
    time_string = datetime.datetime.now()
    print(f"[{time_string}]", *args, **kwargs)


def do_nothing(*args, **kwargs):
    pass


if not enable_debug_logging:
    print_log = do_nothing


def reduce_duplicate_whitespace(text):
    text = text.replace("  ", " ")
    if "  " in text:
        return reduce_duplicate_whitespace(text)
    return text


def iterate_over_events(root, progressbar=False):
    event_lines = []
    weight_ids = []
    weights = []

    tqdm_progressbar = tqdm.tqdm(
        total=len(root), disable=not progressbar, desc="Iterating over LHE events", unit=" events"
    )
    for child in root:
        if child.tag == "event":
            text = reduce_duplicate_whitespace(child.text)
            event_lines.append(text.strip().split("\n"))

            for rwgt in child:
                if rwgt.tag == "rwgt":
                    if weight_ids == []:
                        for wgt in rwgt:
                            weight_ids.append(wgt.attrib["id"])
                    for wgt in rwgt:
                        weights.append(float(wgt.text))
        tqdm_progressbar.update()
    tqdm_progressbar.close()

    return event_lines, weight_ids, weights


def get_event_data_frame(event_lines):
    first_event_lines = [lines[0].strip() for lines in event_lines]
    first_event_line_header = list([str(x) for x in range(6)])

    if len(first_event_lines) == 0:
        return pd.DataFrame(columns=first_event_line_header)

    text = " ".join(first_event_line_header) + "\n" + "\n".join(first_event_lines)
    return pd.read_csv(StringIO(text), sep=" ", index_col=False)


def get_particle_data_frame(event_lines):
    particle_table_lines = []

    for lines in event_lines:
        particle_table_lines.append([l.strip() for l in lines[1:]])

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

    if len(particle_table_lines) == 0:
        return pd.DataFrame(columns=["event"] + event_table_header)

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


def get_reweighting_data_frame(weight_ids, weights):

    if len(weights) == 0:
        return pd.DataFrame()

    weights = np.array(weights)
    n_weights = len(weight_ids)
    return pd.DataFrame(weights.reshape((-1, n_weights)), columns=weight_ids)


class NestedListIterator(object):
    def parse(self, binary_string):
        print_log(f"Parsing XML batch {self.counter_ + 1}...")
        return ET.fromstring(binary_string)

    def __init__(self, nested_list):
        self.iter_outer_ = iter(nested_list)
        self.counter_ = 0
        self.elements_ = self.parse(next(self.iter_outer_))
        self.iter_inner_ = iter(self.elements_)

    def __next__(self):
        try:
            return next(self.iter_inner_)
        except StopIteration:
            del self.elements_
            self.counter_ += 1
            self.elements_ = self.parse(next(self.iter_outer_))
            self.iter_inner_ = iter(self.elements_)
            return next(self.iter_inner_)


class NestedList(object):
    def __init__(self, nested_list, size):
        self.nested_list_ = nested_list
        self.size_ = size

    def __len__(self):
        return self.size_

    def __iter__(self):
        return NestedListIterator(self.nested_list_)


def read_lhe_file(file_handle, batch_size=1000, maxevents=None, progressbar=True):

    header_read = False
    data_header = []

    data = [b"<LesHouchesEvents>"]
    do_batching = not batch_size is None and batch_size > 0
    batch_starts = [1]
    i_event = 0

    # Will be autodetected from the LHE file
    n_events = None
    cross_section = None
    tqdm_progressbar = None

    print_log("Looping over lines in file")

    for line in file_handle:

        if not header_read:

            # This should work with LHE files from madgraph
            if b"nevents" in line and n_events is None:
                line = line.replace("\t", " ")
                n_events = int(line.strip().split(b" ")[0])
                if not maxevents is None and maxevents >= 0:
                    n_events = min(n_events, maxevents)

                # Now we have the knowledge to make a progressbar!
                tqdm_progressbar = tqdm.tqdm(
                    total=n_events, disable=not progressbar, desc="Copying LHE file into memory", unit=" events"
                )

            if b"Integrated weight" in line:
                cross_section = float(line.split(b" ")[-1])

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

            if not tqdm_progressbar is None:
                tqdm_progressbar.update()

    if not tqdm_progressbar is None:
        tqdm_progressbar.close()

    if not batch_starts[-1] == len(data) - 1:
        batch_starts.append(len(data) - 1)

    print_log("Reading header XML from binary string")
    joined_data_header = b"".join(data_header)
    root_header = ET.fromstring(joined_data_header)

    if len(data) == 1:
        return root_header, [], None

    if not do_batching:
        print_log("Joining binary data")
        joined_data = b"".join(data)

        print_log("Reading events XML from binary string")
        root_events = ET.fromstring(joined_data)
    else:
        print_log("Reading events XML by batches")
        root_events_list = []
        for a, b in zip(batch_starts[:-1], batch_starts[1:]):
            print_log(f"...parsing batch {len(root_events_list) + 1}")
            joined_data = b"".join([b"<LesHouchesEvents>"] + data[a:b] + [b"</LesHouchesEvents>"])
            root_events_list.append(joined_data)

        root_events = NestedList(root_events_list, i_event)

    return root_header, root_events, cross_section


class LHEReader(object):
    def __init__(self, lhe_filepath, maxevents=None, batch_size=100, progressbar=True):

        print_log(f"Opening LHE file {lhe_filepath}")

        if lhe_filepath.endswith(".lhe.gz"):
            with gzip.open(lhe_filepath, "r") as f:
                self.header_root_, self.event_root_, self.cross_section_ = read_lhe_file(
                    f, maxevents=maxevents, batch_size=batch_size, progressbar=progressbar
                )
        elif lhe_filepath.endswith(".lhe"):
            with open(lhe_filepath, "rb") as f:
                self.header_root_, self.event_root_, self.cross_section_ = read_lhe_file(
                    f, maxevents=maxevents, batch_size=batch_size, progressbar=progressbar
                )
        else:
            raise RuntimeError(f"File {lhe_filepath} not recognized as LHE file. It should end with .lhe or .lhz.gz")

        print_log("Reading file into XML data structures done")

        self.progressbar_ = progressbar

        # This will get computed once you do the first computation which requires it
        self.event_lines_ = None
        self.weight_ids_ = None
        self.weights_ = None

    def cross_section(self):
        """Return cross section in pb.
        """
        return self.cross_section_

    def _iterate_over_events(self):
        if not self.event_lines_ is None:
            return
        self.event_lines_, self.weight_ids_, self.weights_ = iterate_over_events(
            self.event_root_, progressbar=self.progressbar_
        )

    def event_data_frame(self):
        self._iterate_over_events()
        return get_event_data_frame(self.event_lines_)

    def particle_data_frame(self):
        self._iterate_over_events()
        return get_particle_data_frame(self.event_lines_)

    def reweighting_data_frame(self):
        self._iterate_over_events()
        return get_reweighting_data_frame(self.weight_ids_, self.weights_)
