import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.tree import DecisionTreeClassifier


def _snap_boxes(df):
    for n1 in df.index:
        b1 = df.loc[n1, ["xmin", "xmax", "ymin", "ymax"]]
        for n2 in df.index:
            if n1 == n2:
                continue
            b2 = df.loc[n2, ["xmin", "xmax", "ymin", "ymax"]]

            thresh = 0.2

            d = b1["xmin"] - b2["xmax"]
            if d > 0.0 and d < thresh:
                if (df["xmin"] == b1["xmin"]).sum() > 1:
                    df.loc[n2, "xmax"] = b1["xmin"]
                else:
                    df.loc[n1, "xmin"] = b2["xmax"]

            d = b1["ymin"] - b2["ymax"]
            if d > 0.0 and d < thresh:
                if (df["ymin"] == b1["ymin"]).sum() > 1:
                    df.loc[n2, "ymax"] = b1["ymin"]
                else:
                    df.loc[n1, "ymin"] = b2["ymax"]

    for n1 in df.index:
        b1 = df.loc[n1, ["xmin", "xmax", "ymin", "ymax"]]
        if n1 == 4 or n1 == 5:
            df.loc[n1, "ymax"] = np.inf
        if n1 == 2:
            df.loc[n1, "ymin"] = -np.inf
        if n1 == 0:
            df.loc[n1, "xmin"] = -np.inf

    return df


class RectangularBinningModel(object):
    def __init__(
        self,
        max_depth=5,
        min_samples_bin=1,
        min_rel_s_over_b_improvement=1.5,
        min_rel_signal_uncertainty=0.02,
        min_rel_background_uncertainty=0.08,
        snap_boxes_to_full_phasespace=True,
        override_splitting_test=False,
    ):
        self.max_depth_ = max_depth
        self.min_samples_bin_ = min_samples_bin
        self.min_rel_s_over_b_improvement_ = min_rel_s_over_b_improvement
        self.min_rel_signal_uncertainty_ = min_rel_signal_uncertainty
        self.min_rel_background_uncertainty_ = min_rel_background_uncertainty
        self.snap_boxes_to_full_phasespace_ = snap_boxes_to_full_phasespace
        self.override_splitting_test_ = override_splitting_test
        self.snapped_ = False

    def fit(self, X, y, sample_weight=None):

        if len(X.shape) != 2 or X.shape[1] != 2:
            raise ValueError("RectangularBinningModel only accepts 2D feature space right now!")

        clf = DecisionTreeClassifier(max_depth=self.max_depth_, min_samples_leaf=self.min_samples_bin_)
        clf.fit(X, y, sample_weight=sample_weight)
        tree = clf.tree_

        self.boxes_ = pd.DataFrame(columns=["xmin", "xmax", "ymin", "ymax"])
        i_box = [0]

        start_box = [[-np.inf, np.inf], [-np.inf, np.inf]]

        def apply_box(box):
            return np.logical_and.reduce(
                [X[:, 0] >= box[0][0], X[:, 0] < box[0][1], X[:, 1] >= box[1][0], X[:, 1] < box[1][1]]
            )

        def count_sb(box):
            in_box = apply_box(box)
            s = np.sum(in_box[y == 1])
            b = np.sum(in_box[y == 0])
            return s, b

        def pass_cuts(s, b):
            s_uncert = 1.0 / np.sqrt(s)
            b_uncert = 1.0 / np.sqrt(b)
            return s_uncert < self.min_rel_signal_uncertainty_ and b_uncert < self.min_rel_background_uncertainty_

        def is_worth_splitting(s_left, b_left, s_right, b_right):
            if self.override_splitting_test_:
                return True
            sob1 = 1.0 * s_left / b_left
            sob2 = 1.0 * s_right / b_right
            return max(sob1 / sob2, sob2 / sob1) > self.min_rel_s_over_b_improvement_

        def recurse(node_id, node_depth, box):

            if tree.children_left[node_id] != tree.children_right[node_id]:
                box_left = [box[0][:], box[1][:]]
                box_right = [box[0][:], box[1][:]]

                box_left[tree.feature[node_id]][1] = tree.threshold[node_id]
                box_right[tree.feature[node_id]][0] = tree.threshold[node_id]

                s_left, b_left = count_sb(box_left)
                s_right, b_right = count_sb(box_right)

                if not is_worth_splitting(s_left, b_left, s_right, b_right):
                    self.boxes_.loc[i_box[0], self.boxes_.columns] = *box[0], *box[1]
                    i_box[0] += 1
                    return

                recursed = False
                if pass_cuts(s_left, b_left):
                    recurse(tree.children_left[node_id], node_depth + 1, box_left)
                    recursed = True
                if pass_cuts(s_right, b_right):
                    recurse(tree.children_right[node_id], node_depth + 1, box_right)
                    recursed = True
                if not recursed:
                    self.boxes_.loc[i_box[0], self.boxes_.columns] = *box[0], *box[1]
                    i_box[0] += 1

            else:
                self.boxes_.loc[i_box[0], self.boxes_.columns] = *box[0], *box[1]
                i_box[0] += 1

        recurse(0, 0, start_box)

        if self.snap_boxes_to_full_phasespace_:
            self.boxes_ = _snap_boxes(self.boxes_)
            self.snapped_ = True

        return self

    def visualize(self, limit=10, alpha=1.0):
        df = self.boxes_.copy()
        df.values[df.values == np.inf] = limit
        df.values[df.values == -np.inf] = -limit
        for i_box in df.index:
            x = np.array(df.loc[i_box, ["xmin", "xmax"]], dtype=np.float)
            y = np.array(df.loc[i_box, ["ymin", "ymax"]], dtype=np.float)
            plt.fill_between(x, *y, label=i_box, alpha=alpha)
        plt.xlim(-limit, limit)
        plt.ylim(-limit, limit)

    def apply(self, X):
        out = np.zeros(X.shape[0], dtype=np.int) - 1
        for i_box in self.boxes_.index:
            xlim = self.boxes_.loc[i_box, ["xmin", "xmax"]]
            ylim = self.boxes_.loc[i_box, ["ymin", "ymax"]]
            mask = np.logical_and.reduce([X[:, 0] >= xlim[0], X[:, 0] < xlim[1], X[:, 1] >= ylim[0], X[:, 1] < ylim[1]])

            # if (out[mask] != -1).any():
            # raise ValueError("The boxes are overlapping!")
            out[mask] = i_box

        if self.snapped_ and (out[mask] == -1).any():
            raise ValueError("The boxes were snapped incorrectly, as they don't fill up the full phase space!")

        return out

    def pandas(self):
        return self.boxes_.copy()

    @classmethod
    def from_pandas(cls, df):
        model = cls()
        model.boxes_ = df[["xmin", "xmax", "ymin", "ymax"]]
        return model
