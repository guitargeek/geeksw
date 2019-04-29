import numpy as np


class Cutflow(object):
    @staticmethod
    def frommasks(masks, labels):
        cutflow = Cutflow()
        _mask = np.ones_like(masks[0], dtype=np.bool)
        cutflow._labels = labels
        cutflow._nbegin = len(masks[0])
        efficiencies = []
        _masks = []
        for mask in masks:
            _mask = np.logical_and(_mask, mask)
            _masks.append(_mask)
            efficiencies.append(float(np.sum(_mask)) / cutflow._nbegin)

        cutflow._efficiencies = np.array(efficiencies)
        cutflow._nend = np.sum(_mask)

        cutflow._masks = _masks

        return cutflow

    @property
    def labels(self):
        return self._labels

    @property
    def efficiency(self):
        return self._efficiencies[-1]

    @property
    def nbegin(self):
        return self._nbegin

    @property
    def nend(self):
        return self._nend

    @property
    def efficiencies(self):
        return self._efficiencies

    @property
    def mask(self):
        return self._masks[-1]

    def __call__(self, array):
        if len(array) == len(self._masks[-1]):
            return array[self._masks[-1]]

        for m in self._masks[:len(self._masks) - 1]:
            if np.sum(m) == len(array):
                return array[self._masks[-1][m]]
        raise ValueError("The cutflow can't automatically determine what to do.")

    def __repr__(self):
        s = "<Cutflow"
        for label, eff in zip(self._labels, self._efficiencies):
            if s[-1] != "w":
                s += ","
            s += " (" + label + ", {0:.1f} %)".format(100 * eff)
        s += ">"
        return s

    def prettyprint(self):
        s = "Cutflow:"
        i = 0
        for label, eff in zip(self._labels, self._efficiencies):
            i = i + 1
            s += "\n    " + str(i) + ". " + label + ": {0:.1f} %".format(100 * eff)
        return s

    def __mul__(self, other):
        if self._nend != other._nbegin:
            raise ValueError("cutflows don't seem to match from the number of events")

        cutflow = Cutflow()

        cutflow._labels = self._labels + other._labels
        cutflow._efficiencies = np.concatenate([self._efficiencies, other._efficiencies * self._efficiencies[-1]])
        cutflow._nbegin = self._nbegin
        cutflow._nend = other._nend

        cutflow._masks = [m.copy() for m in self._masks]
        for m in other._masks:
            cutflow._masks.append(self._masks[-1].copy())
            cutflow._masks[-1][cutflow._masks[-1]] = m

        return cutflow

    @property
    def series(self):

        import pandas as pd

        return pd.Series(data=self._efficiencies, index=self._labels)[::-1]

    def plot(self):

        import matplotlib.pyplot as plt
        import pandas as pd

        series = pd.Series(data=self._efficiencies, index=self._labels)[::-1]
        series.plot(kind="barh", fill=False)
        ax = plt.gca()
        xlim = plt.xlim(0.0, 1.0)
        d = xlim[1] - xlim[0]
        i = 0
        for lbl, val in zip(series.index, series.values):
            ax.text(0.02, i - 0.05, lbl + "  " + "{0:.2f} %".format(100 * val))
            i = i + 1
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        plt.grid(False)

    @staticmethod
    def average(cutflows):

        for cf in cutflows[1:]:
            if len(cf._labels) != len(cutflows[0]._labels):
                raise ValueError("Cutflows don't all have the same length")
            for i in range(len(cf._labels)):
                if cf._labels[i] != cutflows[0]._labels[i]:
                    raise ValueError("Cutflow labels don't match")

        cutflow = Cutflow()
        cutflow._labels = cutflows[0]._labels
        cutflow._nbegin = np.sum([cf._nbegin for cf in cutflows])
        cutflow._nend = np.sum([cf._nend for cf in cutflows])

        cutflow._efficiencies = np.sum([cf._efficiencies * cf._nbegin for cf in cutflows], axis=0) / cutflow._nbegin

        return cutflow
