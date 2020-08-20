import unittest

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import numpy as np
import xgboost as xgb

from geeksw.geeklearn.metrics import calibration_curve


class Test(unittest.TestCase):
    def test_calibration_curve(self):

        random_state = 5

        X, y = make_classification(
            n_samples=5000, n_features=10, n_informative=2, random_state=random_state, n_classes=2, weights=[0.5]
        )

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=random_state)

        clf = xgb.XGBClassifier()
        clf.fit(X_train, y_train)

        scores_train = clf.predict_proba(X_train)[:, 1]
        scores_test = clf.predict_proba(X_test)[:, 1]

        x_calib_train, y_calib_train = calibration_curve(y_train, scores_train, curve_type="stitched")
        x_calib_test, y_calib_test = calibration_curve(y_test, scores_test, curve_type="stitched")

        r_train = np.max(np.abs(y_calib_train - x_calib_train))
        r_test = np.max(np.abs(y_calib_test - x_calib_test))


if __name__ == "__main__":

    unittest.main(verbosity=2)
