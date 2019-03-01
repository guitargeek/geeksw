# Colors adapted from https://root.cern.ch/doc/master/classTColor.html

_colors = {
        800 + 0: "#ffcc00",
        800 - 2: "#ffcc33",
        800 + 7: "#ff6600",
        }

class TColor(object):

    def __init__(self, index):
        self.index = index

    def __add__(self, offset):
        return _colors[self.index + offset]

    def __sub__(self, offset):
        return _colors[self.index - offset]

    def __str__(self):
        print(_colors[self.index])
        return _colors[self.index]

kOrange = TColor(800)
