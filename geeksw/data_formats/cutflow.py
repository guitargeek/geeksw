import numpy as np


class CutFlag(object):
    normal = 0
    inverted = 1
    disabled = 2
    # in case a cut can't be inverted or disabled because the information to do so was lost,
    # the cut will be fixed
    fixed = 3

    @staticmethod
    def totext(flag):
        if flag == CutFlag.normal:
            return "normal"
        if flag == CutFlag.inverted:
            return "inverted"
        if flag == CutFlag.disabled:
            return "disabled"
        if flag == CutFlag.fixed:
            return "fixed"
        raise ValueError("{0} is not a valid cut flag".format(flag))


def apply_flag(mask, cut_flag):
    if cut_flag == CutFlag.normal or cut_flag == CutFlag.fixed:
        return mask
    if cut_flag == CutFlag.disabled:
        return np.ones(len(mask), dtype=np.bool)
    if cut_flag == CutFlag.inverted:
        return ~mask


class Cutflow(object):
    @staticmethod
    def frommasks(masks, labels):
        cutflow = Cutflow()

        cutflow._labels = labels
        cutflow._masks = masks
        cutflow._flags = np.zeros(len(cutflow._masks), dtype=np.int) + CutFlag.normal

        cutflow._update_state()

        return cutflow

    @property
    def labels(self):
        return self._labels

    @property
    def efficiency(self):
        return self._efficiencies[-1]

    @property
    def nbegin(self):
        return self._n_events[0]

    @property
    def nend(self):
        return self._n_events[-1]

    @property
    def efficiencies(self):
        return self._efficiencies

    @property
    def masks(self):
        return self._masks

    def total_mask(self, cut_label):
        cut_index = self._labels.index(cut_label)
        mask = np.ones(self.nbegin, dtype=np.bool)

        for i in range(cut_index + 1):
            mask = np.logical_and(mask, apply_flag(self._masks[i], self._flags[i]))
        return mask

    def __call__(self, array, cut_label=None):

        if array is None:
            return None

        if cut_label is None:
            cut_label = self._labels[-1]

        cut_index = self._labels.index(cut_label)

        mask_prev = np.ones(self.nbegin, dtype=np.bool)

        match = False

        for i in range(cut_index + 1):
            if len(array) == self._n_events[i]:
                if match:
                    raise ValueError("Ambiguity error when calling cutflow!!")
                masks = [apply_flag(m, self._flags[i + j]) for j, m in enumerate(self._masks[i : cut_index + 1])]
                mask = np.logical_and.reduce(masks)
                match = True
            if not match:
                mask_prev = np.logical_and(mask_prev, apply_flag(self._masks[i], self._flags[i]))
        if match:
            return array[mask[mask_prev]]
        if len(array) == self.nend:
            return array

        raise ValueError("The cutflow can't automatically determine what to do.")

    def _update_state(self):

        self._n_events = [len(self._masks[0])]

        efficiencies = []
        n_events = [self.nbegin]

        total_mask = np.ones(self.nbegin, dtype=np.bool)

        for mask, flag in zip(self._masks, self._flags):
            total_mask = np.logical_and(total_mask, apply_flag(mask, flag))
            n_remaining = np.sum(total_mask)
            efficiencies.append(float(n_remaining) / self.nbegin)
            n_events.append(n_remaining)

        self._efficiencies = np.array(efficiencies)
        self._n_events = np.array(n_events)

    def invert(self, cut_label):
        cut_index = self._labels.index(cut_label)
        if self._flags[cut_index] == CutFlag.fixed:
            raise ValueError("cut " + cut_label + " can't be toggled, the information to do so was lost.")
        if self._flags[cut_index] == CutFlag.disabled:
            raise ValueError("cut " + cut_label + " can't be toggled because it's disabled.")

        if self._flags[cut_index] == CutFlag.normal:
            self._flags[cut_index] = CutFlag.inverted
            self._update_state()
        elif self._flags[cut_index] == CutFlag.inverted:
            self._flags[cut_index] = CutFlag.normal
            self._update_state()

    def disable(self, cut_label):
        cut_index = self._labels.index(cut_label)
        if self._flags[cut_index] == CutFlag.fixed:
            raise ValueError("cut " + cut_label + " can't be disabled, the information to do so was lost.")

        if self._flags[cut_index] == CutFlag.inverted:
            self.invert(cut_label)

        self._flags[cut_index] = CutFlag.disabled
        self._update_state()

    def enable(self, cut_label):
        cut_index = self._labels.index(cut_label)
        if self._flags[cut_index] == CutFlag.fixed or self._flags[cut_index] == CutFlag.normal:
            return

        self._flags[cut_index] = CutFlag.normal
        self._update_state()

    def __repr__(self):
        s = "<Cutflow"
        for label, eff, flag in zip(self._labels, self._efficiencies, self._flags):
            if s[-1] != "w":
                s += ","
            if eff * 100 > 0.01:
                s += " (" + label + ": {0:.4f} %)".format(eff * 100) + " (" + CutFlag.totext(flag) + ")"
            else:
                s += " (" + label + ": {0:.2e})".format(eff) + " (" + CutFlag.totext(flag) + ")"
        s += ">"
        return s

    def __str__(self):
        s = "Cutflow:"
        i = 0
        for label, eff, flag in zip(self._labels, self._efficiencies, self._flags):
            i = i + 1
            if eff * 100 > 0.01:
                eff_str = "{0:.4f} %)".format(eff * 100)
            else:
                eff_str = "{0:.2e})".format(eff)
            s += "\n    " + str(i) + ". " + label + ": " + eff_str + " (" + CutFlag.totext(flag) + ")"
        return s

    def __mul__(self, other):

        cutflow = Cutflow()

        cutflow._labels = self._labels + other._labels
        cutflow._flags = np.zeros(len(cutflow._labels), dtype=np.int) + CutFlag.normal

        joined = False

        total_mask = np.ones(self.nbegin, dtype=np.bool)

        for i, n_events_i in enumerate(self._n_events):
            if n_events_i == other.nbegin:
                if joined:
                    raise ValueError("ambiguity error in cutflow!!")
                cutflow._masks = [m.copy() for m in self._masks]
                for m in other._masks:
                    cutflow._masks.append(total_mask.copy())
                    cutflow._masks[-1][total_mask] = m
                joined = True
            if not joined:
                cutflow._flags[i] = CutFlag.fixed
            if i < len(self._masks):
                total_mask = np.logical_and(total_mask, self._masks[i])

        if not joined:
            raise ValueError("cutflows don't seem to match from the number of events")

        cutflow._update_state()

        return cutflow

    def series(self):

        import pandas as pd

        return pd.Series(data=self._efficiencies, index=self._labels)

    def pandas(self):

        import pandas as pd

        return pd.DataFrame(dict(efficiency=self._efficiencies, label=self._labels))

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
        cutflow._n_events = np.sum([cf._n_events for cf in cutflows], axis=0)

        cutflow._efficiencies = np.sum([cf._efficiencies * cf.nbegin for cf in cutflows], axis=0) / cutflow.nbegin

        return cutflow
