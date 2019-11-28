import numpy as np
from sklearn.model_selection import cross_validate
from bayes_opt import BayesianOptimization
from sklearn.base import clone

from ..functools import *


class BayesianOptimizationCV:
    def __init__(
        self,
        estimator,
        param_boundaries,
        int_params=[],
        init_points=2,
        n_iter=10,
        cv=None,
        scoring=None,
        random_state=None,
        return_train_score=False,
        verbose=2,
    ):
        if n_iter < init_points:
            raise ValueError("n_iter has to be larger than init_points.")

        self._estimator = estimator
        self._param_boundaries = param_boundaries
        self._int_params = int_params
        self._init_points = init_points
        self._n_iter = n_iter - init_points
        self._cv = cv
        self._scoring = scoring
        self._random_state = random_state
        self._return_train_score = return_train_score
        self._verbose = verbose

    def fit(self, X, y):

        cv_results = {}

        def target(**kwargs):

            for name in self._int_params:
                kwargs[name] = int(kwargs[name])

            model = clone(self._estimator).set_params(**kwargs)
            cv_result = cross_validate(
                model,
                X,
                y,
                cv=self._cv,
                scoring=self._scoring,
                return_train_score=self._return_train_score,
                verbose=self._verbose - 2,
            )

            n_cv = len(cv_result["test_score"])

            for name, values in cv_result.items():

                if not "mean_" + name in cv_results:
                    if name not in ["fit_time", "score_time"]:
                        for i in range(n_cv):
                            cv_results["split" + str(i) + "_" + name] = []
                    cv_results["mean_" + name] = []
                    cv_results["std_" + name] = []

                if name not in ["fit_time", "score_time"]:
                    for i in range(n_cv):
                        cv_results["split" + str(i) + "_" + name].append(values[i])
                cv_results["mean_" + name].append(np.mean(values))
                cv_results["std_" + name].append(np.std(values))

            return cv_results["mean_test_score"][-1]

        optimizer = BayesianOptimization(
            f=target, pbounds=self._param_boundaries, random_state=self._random_state, verbose=self._verbose
        )

        optimizer.maximize(init_points=self._init_points, n_iter=self._n_iter, acq="ei")

        for i, d in enumerate(optimizer.res):

            for name in self._int_params:
                d["params"][name] = int(d["params"][name])

            for name, value in d["params"].items():
                if not "param_" + name in cv_results:
                    cv_results["param_" + name] = np.zeros(len(optimizer.res))
                cv_results["param_" + name][i] = value
            if not "params" in cv_results:
                cv_results["params"] = []
            cv_results["params"].append(d["params"])

        indices = list(range(len(cv_results["mean_test_score"])))
        indices.sort(key=lambda x: -cv_results["mean_test_score"][x])
        cv_results["rank_test_score"] = np.zeros(len(indices), dtype=np.int32)
        for i, x in enumerate(indices):
            cv_results["rank_test_score"][x] = i + 1

        for k, v in cv_results.items():
            if type(v) == list and not k == "params":
                cv_results[k] = np.array(v)

        self.cv_results_ = {}

        keywords = ["_time", "param", "_test_"]
        for keyword in keywords:
            for k, v in cv_results.items():
                if keyword in k:
                    self.cv_results_[k] = v

        for k, v in cv_results.items():
            if not anymap(contains, keywords, k):
                self.cv_results_[k] = v
