# Colors adapted from https://root.cern.ch/doc/master/classTColor.html

tcolor = {
    0: "#ffffff",
    1: "#000000",
    2: "#ff0000",
    3: "#00ff00",
    4: "#0000ff",
    5: "#ffff00",
    6: "#ff00ff",
    7: "#00ffff",
    8: "#59d354",
    9: "#5954d8",
    10: "#fefefe",
    11: "#c0b6ac",
    12: "#4c4c4c",
    13: "#666666",
    14: "#7f7f7f",
    15: "#999999",
    16: "#b2b2b2",
    17: "#cccccc",
    18: "#e5e5e5",
    19: "#f2f2f2",
    20: "#ccc6aa",
    21: "#ccc6aa",
    22: "#c1bfa8",
    23: "#bab5a3",
    24: "#b2a596",
    25: "#b7a39b",
    26: "#ad998c",
    27: "#9b8e82",
    28: "#876656",
    29: "#afcec6",
    30: "#84c1a3",
    31: "#89a8a0",
    32: "#829e8c",
    33: "#adbcc6",
    34: "#7a8e99",
    35: "#758991",
    36: "#688296",
    37: "#6d7a84",
    38: "#7c99d1",
    39: "#7f7f9b",
    40: "#aaa5bf",
    41: "#d3ce87",
    42: "#ddba87",
    43: "#bc9e82",
    44: "#c6997c",
    45: "#bf8277",
    46: "#ce5e60",
    47: "#aa8e93",
    48: "#a5777a",
    49: "#936870",
    416: "#00ff00",
    417: "#00cc00",
    418: "#009900",
    419: "#006600",
    420: "#003300",
    432: "#00ffff",
    433: "#00cccc",
    800: "#ffcc00",
    798: "#ffcc33",
    807: "#ff6600",
    840: "#00ffcc",
    920: "#cccccc",
    921: "#999999",
    922: "#666666",
    923: "#333333",
}


class TColor(object):
    def __init__(self, index):
        self.index = index

    def __add__(self, offset):
        return tcolor[self.index + offset]

    def __sub__(self, offset):
        return tcolor[self.index - offset]

    def __str__(self):
        return tcolor[self.index]


kWhite = TColor(0)
kBlack = TColor(1)
kYellow = TColor(400)
kGreen = TColor(416)
kCyan = TColor(432)
kBlue = TColor(600)
kMagenta = TColor(616)
kRed = TColor(632)
kOrange = TColor(800)
kSpring = TColor(820)
kTeal = TColor(840)
kAzure = TColor(860)
kViolet = TColor(880)
kPink = TColor(900)
kGray = TColor(920)
