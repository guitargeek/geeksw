import os.path
import itertools
import glob

# these should be the geeksw internal dataset paths.
datasets = [
        "/2016/mc/ZEE/",
        "/2016/mc/TTBar/",
        "/2016/mc/QCD/",
        "/2016/data/",
        "/2017/mc/ZEE/",
        "/2017/mc/TTBar/",
        "/2017/mc/QCD/",
        "/2017/data/",
        ]

# tuple of what producers require and produce.
# No requirement implies the producer starts from the dataset.
# No "/" at the beginning of the path implies a relative path which is
# automatically resolved (equivalent to "/**/")

class Producer(object):

    def __init__(self, requires, produces):

        self.requires = requires
        self.produces = produces

        # # this will get auto-inferred later
        # self.working_dir = None

producers = [
             Producer([],                       ["pt", "eta", "phi"]),
             Producer(["mc/*/m4l", "data/m4l"], ["plots/m4l"]),
             Producer(["pt", "eta", "phi"],     ["m4l"]             ),
             # Producer(["*/data/m4l"],           ["plots/data/m4l"]),
            ]

targets = [
           "/2016/plots/m4l", # comparing m4l in data with mc in 2016
           "/2017/plots/m4l", # comparing m4l in data with mc in 2017
           # "/plots/data/m4l", # comparing m4l in data over the years
          ]

def path_product(p1, p2):
    return [os.path.join(*x) for x in itertools.product(p1, p2)]

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Create the output dir structure
out_dir = "out"
for ds in datasets:
    mkdir(os.path.join(out_dir, "."+ds))

def get_matching_producer(target, producers):
    """ Takes a target product identifier and a list of producers.

        Returns the index of the producer whose products matches best with the
        target and the directory the producer has to work on to produce the
        target.
    """

    matching_chars = 0
    producer = None
    working_dir = None

    for i, p in enumerate(producers):
        for prod in p.produces:
            t = target[-len(prod):]
            if t == prod:
                if len(t) > matching_chars:
                    producer = p
                    matching_chars = len(t)
                    working_dir = target[:-len(prod)]

    return producer, working_dir

for t in targets:
    print("Target "+t)
    print(get_matching_producer(t, producers))
    print("")

"""
# First, expand the products using the datasets
for p in producers:
    if p.requires == []:
        p.produces = path_product(datasets, p.produces)

        # print(p[1])

for p in producers:
    print(p.requires)
    print(p.produces)
    print("")
"""
