import pickle
import os

def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

class Plot(object):
    def __init__(self, **kwargs):
        import matplotlib.pyplot as plt
        self.figure_handle = plt.figure(**kwargs)

    def commit(self):
        self.dump = pickle.dumps(self.figure_handle)

    def save(self, path, name):
        size = 0

        self.figure_handle = pickle.loads(self.dump)

        mkdir(os.path.join(path, "pkl"))
        mkdir(os.path.join(path, "png"))
        mkdir(os.path.join(path, "pdf"))

        print(path)
        print(name)

        file_name = os.path.join(path, "pkl", name + ".pkl")
        with open( file_name, "wb" ) as f:
            pickle.dump(self.figure_handle, f)
        size += os.path.getsize(file_name)
        file_name = os.path.join(path, "png", name + ".png")
        self.figure_handle.savefig(file_name, dpi=300)
        size += os.path.getsize(file_name)
        file_name = os.path.join(path, "pdf", name + ".pdf")
        self.figure_handle.savefig(file_name)
        size += os.path.getsize(file_name)
        return size
