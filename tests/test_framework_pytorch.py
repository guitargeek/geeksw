import unittest
import torch
import numpy as np
import shutil

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

import geeksw.framework as fwk

cache_dir = ".test_framework_cache"


class Test(unittest.TestCase):
    def test_framework_pytorch(self):

        # Make sure there is no cache so far
        try:
            shutil.rmtree(cache_dir)
        except:
            pass

        X, y = make_classification(n_samples=100000, n_features=20, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

        X_train = torch.tensor(X_train, dtype=torch.double)
        X_test = torch.tensor(X_test, dtype=torch.double)

        y_train = torch.tensor(y_train, dtype=torch.long)
        y_test = torch.tensor(y_test, dtype=torch.long)

        loss_fn = torch.nn.NLLLoss()

        @fwk.one_producer("model")
        def model_producer():

            model = torch.nn.Sequential(
                torch.nn.Linear(20, 20),
                torch.nn.ReLU(),
                torch.nn.Linear(20, 8),
                torch.nn.ReLU(),
                torch.nn.Linear(8, 2),
                torch.nn.LogSoftmax(),
            ).double()

            learning_rate = 1e-3
            optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

            batch_size = 256
            epochs = 1

            minibatch_ranges = list(range(0, len(X_train), batch_size)) + [len(X_train)]
            minibatch_ranges = list(zip(minibatch_ranges[:-1], minibatch_ranges[1:]))

            for epoch in range(epochs):
                losses = []
                for start, stop in minibatch_ranges:
                    y_pred = model(X_train[start:stop])

                    loss = loss_fn(y_pred, y_train[start:stop])

                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    losses.append(loss.data.mean())

                train_loss = np.mean(losses)

                print("[%d/%d]  Train loss: %.3f" % (epoch + 1, epochs, train_loss))

            return model

        record = fwk.produce(products=["/model"], producers=[model_producer], cache_time=0.0, cache_dir=cache_dir)

        model = record["model"]

        y_pred = model(X_test)
        model_loss = loss_fn(y_pred, y_test).item()

        del model

        record = fwk.produce(products=["/model"], producers=[model_producer], cache_time=0.0, cache_dir=cache_dir)

        loaded_model = record["model"]

        y_pred = loaded_model(X_test)
        loaded_model_loss = loss_fn(y_pred, y_test).item()

        self.assertEqual(loaded_model_loss, model_loss)

        shutil.rmtree(cache_dir)


if __name__ == "__main__":

    unittest.main(verbosity=2)
