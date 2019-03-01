from matplotlib.pyplot import *

def _initialize():
    matplotlib.rcParams['font.family']         = 'Helvetica'
    matplotlib.rcParams['legend.fontsize']     = 18.0
    matplotlib.rcParams['mathtext.default']    = "regular" # The default font to use for math, default it.
    matplotlib.rcParams['axes.labelsize']      = 21.5      # fontsize of the x any y labels, default medium
    matplotlib.rcParams['xtick.top']           = False     # draw ticks on the top side
    matplotlib.rcParams['xtick.major.size']    = 11        # major tick size in points
    matplotlib.rcParams['xtick.minor.size']    = 5         # minor tick size in points
    matplotlib.rcParams['xtick.minor.visible'] = True
    matplotlib.rcParams['xtick.direction']     = "in"
    matplotlib.rcParams['xtick.labelsize']     = 18.0
    matplotlib.rcParams['ytick.right']         = False     # draw ticks on the right side
    matplotlib.rcParams['ytick.major.size']    = 14        # major tick size in points
    matplotlib.rcParams['ytick.minor.size']    = 8         # minor tick size in points
    matplotlib.rcParams['ytick.minor.visible'] = True
    matplotlib.rcParams['ytick.direction']     = "in"
    matplotlib.rcParams['ytick.labelsize']     = 18.0
    matplotlib.rcParams['legend.handlelength'] = 1.0       # the length of the legend lines
    matplotlib.rcParams['legend.edgecolor']    = "#ffffff"


_figure = figure

def figure(*args, **kwargs):
    if not "figsize" in kwargs:
        kwargs["figsize"] = (8.57, 6.04)
    return _figure(*args, **kwargs)


_xlabel = xlabel

def xlabel(*args, **kwargs):
    if not "horizontalalignment" in kwargs:
        kwargs["horizontalalignment"] = "right"
    if not "x" in kwargs:
        kwargs["x"] = 1.0
    if not "labelpad" in kwargs:
        kwargs["labelpad"] = 0.0
    return _xlabel(*args, **kwargs)

_ylabel = ylabel

def ylabel(*args, **kwargs):
    if not "horizontalalignment" in kwargs:
        kwargs["horizontalalignment"] = "right"
    if not "y" in kwargs:
        kwargs["y"] = 1.0
    if not "labelpad" in kwargs:
        kwargs["labelpad"] = 5.0
    return _ylabel(*args, **kwargs)

def lumitext(s):
    x0, x1 = xlim()
    y0, y1 = ylim()
    return text(x0+(x1 - x0) * 1, y0+(y1 - y0) * 1.025, s,
                fontweight="regular", horizontalalignment='right', fontsize=18)

def cmstext(s, loc=0):
    s1, *s2 = s.split(" ")
    s2 = " ".join(s2)
    x0, x1 = xlim()
    y0, y1 = ylim()
    if loc == 0:
        text(x0+(x1 - x0) * 0.04, y0+(y1 - y0) * 0.84, s2, style="italic", fontsize=16.5)
        return text(x0+(x1 - x0) * 0.04, y0+(y1 - y0) * 0.92, s1, fontweight="bold", fontsize=22)
    if loc == 1:
        text(x1-(x1 - x0) * 0.04, y0+(y1 - y0) * 0.84, s2,
             style="italic", fontsize=16.5, horizontalalignment="right")
        return text(x1-(x1 - x0) * 0.04, y0+(y1 - y0) * 0.92, s1,
                    fontweight="bold", fontsize=22, horizontalalignment="right")
    if loc == 2:
        text(x0+(x1 - x0) * 0.115, y0+(y1 - y0) * 1.025, s2, style="italic", fontsize=16.5)
        return text(x0+(x1 - x0) * 0, y0+(y1 - y0) * 1.025, s1, fontweight="bold", fontsize=22)

_initialize()
