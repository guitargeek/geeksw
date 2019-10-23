from matplotlib.pyplot import *


def _initialize():
    matplotlib.rcParams["font.family"] = "Helvetica"
    matplotlib.rcParams["legend.fontsize"] = 18.0
    matplotlib.rcParams["mathtext.default"] = "regular"  # The default font to use for math, default it.
    matplotlib.rcParams["axes.labelsize"] = 21.5  # fontsize of the x any y labels, default medium
    matplotlib.rcParams["xtick.top"] = False  # draw ticks on the top side
    matplotlib.rcParams["xtick.major.size"] = 11  # major tick size in points
    matplotlib.rcParams["xtick.minor.size"] = 5  # minor tick size in points
    matplotlib.rcParams["xtick.minor.visible"] = True
    matplotlib.rcParams["xtick.direction"] = "in"
    matplotlib.rcParams["xtick.labelsize"] = 18.0
    matplotlib.rcParams["ytick.right"] = False  # draw ticks on the right side
    matplotlib.rcParams["ytick.major.size"] = 14  # major tick size in points
    matplotlib.rcParams["ytick.minor.size"] = 8  # minor tick size in points
    matplotlib.rcParams["ytick.minor.visible"] = True
    matplotlib.rcParams["ytick.direction"] = "in"
    matplotlib.rcParams["ytick.labelsize"] = 18.0
    matplotlib.rcParams["legend.handlelength"] = 1.0  # the length of the legend lines
    matplotlib.rcParams["legend.edgecolor"] = "#ffffff"


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
    return text(
        x0 + (x1 - x0) * 1, y0 + (y1 - y0) * 1.025, s, fontweight="regular", horizontalalignment="right", fontsize=18
    )


def cmstext(s, loc=0):
    s1, *s2 = s.split(" ")
    s2 = " ".join(s2)
    x0, x1 = xlim()
    y0, y1 = ylim()
    if loc == 0:
        text(x0 + (x1 - x0) * 0.04, y0 + (y1 - y0) * 0.84, s2, style="italic", fontsize=16.5)
        return text(x0 + (x1 - x0) * 0.04, y0 + (y1 - y0) * 0.92, s1, fontweight="bold", fontsize=22)
    if loc == 1:
        text(
            x1 - (x1 - x0) * 0.04, y0 + (y1 - y0) * 0.84, s2, style="italic", fontsize=16.5, horizontalalignment="right"
        )
        return text(
            x1 - (x1 - x0) * 0.04,
            y0 + (y1 - y0) * 0.92,
            s1,
            fontweight="bold",
            fontsize=22,
            horizontalalignment="right",
        )
    if loc == 2:
        text(x0 + (x1 - x0) * 0.115, y0 + (y1 - y0) * 1.025, s2, style="italic", fontsize=16.5)
        return text(x0 + (x1 - x0) * 0, y0 + (y1 - y0) * 1.025, s1, fontweight="bold", fontsize=22)


def cms_hist(
    values,
    bins,
    weights=None,
    plot_uncertainty=True,
    style="mc",
    color=None,
    fill=True,
    baseline_events=None,
    baseline_errors2=None,
    **kwargs
):

    if not weights is None:
        counts = np.histogram(values, bins=bins)[0]
        events = np.histogram(values, weights=weights, bins=bins)[0]
        errors2 = np.divide(events ** 2, counts, out=np.zeros_like(events), where=counts != 0)
    else:
        events = np.histogram(values, bins=bins)[0]
        errors2 = events

    if not baseline_events is None:
        events = events + baseline_events
    if not baseline_errors2 is None:
        errors2 = errors2 + baseline_errors2

    errors = np.sqrt(errors2)

    if style == "mc":
        x = np.vstack([bins, bins]).T.flatten()

        def to_y(events):
            return np.concatenate([[0.0], np.vstack([events, events]).T.flatten(), [0.0]])

        if fill:
            y_low = 0.0 if baseline_events is None else to_y(baseline_events)
            fill_between(x, y_low, to_y(events), facecolor=color, edgecolor="k", linewidth=1.0, **kwargs)
        else:
            plot(x, to_y(events), color="k" if fill else color, linewidth=2.0, **kwargs)

        if plot_uncertainty:
            fill_between(
                x,
                to_y(events - errors),
                to_y(events + errors),
                hatch="\\\\\\\\\\",
                facecolor="none",
                edgecolor="k",
                linewidth=0.0,
                alpha=0.5,
            )
    if style == "data":
        bin_centers = (bins[1:] + bins[:-1]) / 2.0
        y = np.array(events, dtype=np.float)
        yerr = errors
        yerr[y == 0] = np.nan
        y[y == 0] = np.nan
        if plot_uncertainty:
            errorbar(bin_centers, y, yerr=yerr, color="k", fmt="o", **kwargs)
        else:
            scatter(bin_centers, y, color="k", **kwargs)

    return events, errors2


set_xlabel = xlabel
set_ylabel = ylabel


def finalize(bins, xlabel=None, ylabel="Events", n_legend_cols=1):
    xlim(bins[0], bins[-1])
    ylim(0, ylim()[-1])

    cmstext("CMS Simulation", loc=2)
    lumitext("137 $fb^{-1}$ (13 TeV)")

    if xlabel:
        set_xlabel(xlabel)

    if ylabel:
        set_ylabel(ylabel)

    if n_legend_cols > 0:
        legend(ncol=n_legend_cols)


_initialize()
