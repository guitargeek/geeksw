import numpy as np
from sklearn.tree import DecisionTreeClassifier
from scipy.optimize import minimize_scalar


class PairwiseLikelihoodRatioModel(object):
    def __init__(self, n_bins=3):
        self._n_bins = n_bins

    def train(self, X, y, weights=None):

        # assert the input has the appropriate shape to be a binary score matrix
        assert len(X.shape) == 3
        assert X.shape[1] == X.shape[2]

        # determine the number of classes
        self._n_classes = X.shape[1]

        # assert that the probabilities are normalized,
        # i.e. that the binary score matrices for each event are symmetric
        for i in range(self._n_classes):
            for j in range(i):
                np.testing.assert_allclose(X[:, i, j], -X[:, j, i])

        # create empty lists to hold the histograms and binning
        self._bins = []
        self._r_hist = []

        for i in range(self._n_classes):
            self._bins.append([])
            self._r_hist.append([])

            for j in range(self._n_classes):
                self._bins[-1].append(None)
                self._r_hist[-1].append(None)

        # fill the histograms for each pair is neccessary
        for i in range(self._n_classes):
            for j in range(self._n_classes):
                if i >= j:
                    continue

                s = X[:, i, j]

                thresholds = []
                if self._n_bins > 1:
                    # if there should be more then one bin
                    # (which would mean to not use the classification info at all),
                    # find the binning by extracting the leaf boundaries of a desicion tree
                    # with as many leafs as there should be bins
                    decision_tree = DecisionTreeClassifier(max_leaf_nodes=self._n_bins)
                    mask = np.logical_or(y == i, y == j)
                    decision_tree.fit(s[mask].reshape(-1, 1), y[mask] == j)
                    tree = decision_tree.tree_
                    thresholds = np.sort(tree.threshold[tree.children_left != tree.children_right])
                    # thresholds = [0.]

                # complete the bin array by putting the min and max of the scores at the edges
                self._bins[i][j] = np.concatenate([[np.min(X)], thresholds, [np.max(X) + 1e-6]])

                # get the histograms of the scores for the requested components
                hist_i, _ = np.histogram(s[y == i], bins=self._bins[i][j])
                hist_j, _ = np.histogram(s[y == j], bins=self._bins[i][j])

                # normalize the histogram
                # (remember absolute normalization comes into play only with the component weights)
                hist_i = hist_i / np.sum(hist_i)
                hist_j = hist_j / np.sum(hist_j)

                # fill histograms with likelihood ratios
                self._r_hist[i][j] = hist_j / hist_i

                # assert if likelihood ratios are monotonically decreasing
                # if (np.diff(self._r_hist[i][j]) > 0).any():
                #    raise ValueError("Likelihood ratios are not monotonically decreasing! This should not be the case.")

                # use symmetry of classifcation scores (which has been asserted above)
                # to also fill bins and histogram at the transposed element
                self._bins[j][i] = -self._bins[i][j][::-1]
                self._r_hist[j][i] = (hist_i / hist_j)[::-1]

            # the weights for each component in the calibration sample
            self._weights = np.array([float(np.sum(y == i)) for i in range(self._n_classes)])
            self._n_0 = np.sum(self._weights)
            self._weights /= np.sum(self._weights)

        return self

    def predict(self, X):

        # assert the input has the appropriate shape to be a binary score matrix
        assert len(X.shape) == 3
        assert X.shape[1] == X.shape[2]

        # is the numer of classes as in the training sample?
        assert self._n_classes == X.shape[1]

        # assert that the probabilities are normalized,
        # i.e. that the binary score matrices for each event are symmetric
        for i in range(self._n_classes):
            for j in range(i):
                np.testing.assert_allclose(X[:, i, j], -X[:, j, i])

        # the likelihood ratio will be initialized with ones,
        # as that's how  the diagonal should be by definition
        r = np.ones((X.shape[0], self._n_classes, self._n_classes))

        # loop over the pairs
        for i in range(self._n_classes):
            for j in range(self._n_classes):
                if i >= j:
                    continue
                s = X[:, i, j]

                # determine the bin in which the event resides
                bins = np.digitize(s, self._bins[i][j]) - 1

                # it can happen the event lies out of the original bin range,
                # in which case we just put it into the outer bins by clipping
                bins_clipped = np.clip(bins, 0, len(self._r_hist[i][j]) - 1)

                # get the likelihood ratios from the histograms
                r[:, i, j] = self._r_hist[i][j][bins_clipped]

                # again, exploit symmetry
                r[:, j, i] = 1.0 / r[:, i, j]

        return r

    def make_likelihood_function(self, X):

        r = self.predict(X)
        n_tot = len(X)
        n_0 = self._n_0
        w_0 = self._weights

        def likelihood(mu, unsummed=False):
            w_1 = np.copy(w_0) * n_0

            w_1[0] *= mu
            n_1 = np.sum(w_1)
            w_1 /= np.sum(w_1)

            w_r = np.zeros((self._n_classes, self._n_classes))
            for i in range(self._n_classes):
                for j in range(self._n_classes):
                    w_r[i, j] = w_1[j] / w_0[i]

            extended = float(n_tot) * (np.log(n_0) - np.log(n_1)) - n_0 + n_1

            inner_sum = 1.0 / np.sum(w_r * r, axis=-1)

            l_ratios = np.sum(inner_sum, axis=-1)

            if unsummed:
                return np.log(l_ratios), extended

            return np.sum(np.log(l_ratios)) + extended

        return likelihood


def minimize_likelihood(likelihood_func, bounds=(0.01, 10.0)):
    fit_result = minimize_scalar(likelihood_func, method="Bounded", bounds=bounds)

    value = fit_result.fun
    best_mu = fit_result.x

    fit_result = minimize_scalar(
        lambda x: (likelihood_func(x) - value - 0.5) ** 2, method="Bounded", bounds=(0.01, best_mu)
    )
    lower_mu = fit_result.x

    fit_result = minimize_scalar(
        lambda x: (likelihood_func(x) - value - 0.5) ** 2, method="Bounded", bounds=(best_mu, 10.0)
    )
    upper_mu = fit_result.x

    return best_mu, np.array([lower_mu, upper_mu])
