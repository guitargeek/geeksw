import unittest

import numpy as np

from geeksw.utils import reweighting


np.random.seed = 100


class Test(unittest.TestCase):
    def test_reweight1d_to_flat(self):
        """Test the 1d reweighting to a flat distribution.
        """

        # The tolerance of the test
        tol_mu = 0.1
        tol_std = 0.1

        # Sample size for signal and background
        n = 100000

        # Gaussian signal
        sig = np.random.normal(loc=2.0, scale=1.0, size=n)

        # Calculate weights
        weights = reweighting.reweight1d(sig, bins=200)

        # Calculate reweighted histogram
        bins = np.linspace(-2, 7, 200)
        h, _ = np.histogram(sig, bins=bins)
        h_w, _ = np.histogram(sig, bins=bins, weights=weights)

        # Calculate the relative uncertainty
        # we equate zero counts to one count to get a finite relaive uncertainty
        uncert = 1 / np.sqrt(np.clip(h, a_min=1, a_max=None))

        # print(np.polyfit(bins[:-1], h, deg=1))

        # Calculate the reduced chi2 of the flat hypethesis
        chi2 = np.sum((np.divide(h_w - 1, h_w * uncert, out=np.zeros_like(h_w), where=h_w != 0)) ** 2) / 200

        print("")
        print("Reduced chi2 of flat hypethesis: {:.4f}".format(chi2))

        self.assertTrue(chi2 < 2.0)

    def test_reweight1d_to_ref_dist(self):
        """Test the 1d reweighting to a reference distribution.
        """

        # The tolerance of the test
        tol_mu = 0.1
        tol_std = 0.5

        # Sample size for signal and background
        n = 100000

        # Exponential background
        bkg = np.random.exponential(scale=1.0, size=n)
        # Gaussian signal
        sig = np.random.normal(loc=2.0, scale=1.0, size=n)

        # Calculate weights
        w_sig, w_bkg = reweighting.reweight1d(sig, bkg, bins=200, get_w_ref=True)

        # Calculate reweighted histogram
        bins = np.linspace(-2, 7, 200)
        h_sig, _ = np.histogram(sig, bins=bins, weights=w_sig)
        h_bkg, _ = np.histogram(bkg, bins=bins, weights=w_bkg)

        pulls = np.divide(h_sig - h_bkg, h_bkg ** 0.5, out=np.zeros_like(h_bkg), where=h_bkg != 0)
        mu, std = np.mean(pulls), np.std(pulls)

        print("")
        print("Mean of pull distribution: {:.4f}".format(mu))
        print("Std of pull distribution : {:.4f}".format(std))

        print("Checking if mean is withing 0.0 +/- 0.1 and std within 1.0 +/- 0.1")
        self.assertTrue(abs(mu) < tol_mu and abs(1 - std) < tol_std)

    # def test_reweight2d_to_ref_dist(self):
        # """Test the 2d reweighting to a reference distribution.
        # """

        # # The tolerance of the test
        # tol_mu = 0.1
        # tol_std = 0.5

        # # Sample size for signal and background
        # n = 1000000

        # # Exponential background
        # bkg_x = np.random.exponential(scale=1.0, size=n)
        # bkg_y = np.random.exponential(scale=1.1, size=n)
        # # Gaussian signal
        # sig_x = np.random.normal(loc=2.0, scale=1.0, size=n)
        # sig_y = np.random.normal(loc=2.5, scale=1.5, size=n)

        # # Calculate weights
        # w_sig, w_bkg = reweighting.reweight2d(sig_x, sig_y, bkg_x, bkg_y, x_bins=100, y_bins=100, get_w_ref=True)

        # # Calculate reweighted histogram (x axis)
        # bins = np.linspace(0, 5, 10)
        # h_sig, _ = np.histogram(sig_x, bins=bins, weights=w_sig)
        # h_bkg, _ = np.histogram(bkg_x, bins=bins, weights=w_bkg)

        # # check if relative differences to reference are smaller than 2 %
        # r = np.divide(h_sig - h_bkg, h_bkg, out=np.zeros_like(h_bkg), where=h_bkg != 0)
        # assert (np.abs(r) < 0.02).all()

        # # Calculate reweighted histogram (y axis)
        # bins = np.linspace(0, 7, 10)
        # h_sig, _ = np.histogram(sig_y, bins=bins, weights=w_sig)
        # h_bkg, _ = np.histogram(bkg_y, bins=bins, weights=w_bkg)

        # # check if relative differences to reference are smaller than 2 %
        # r = np.divide(h_sig - h_bkg, h_bkg, out=np.zeros_like(h_bkg), where=h_bkg != 0)
        # assert (np.abs(r) < 0.02).all()


if __name__ == "__main__":

    unittest.main(verbosity=2)
