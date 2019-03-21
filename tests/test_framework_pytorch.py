import unittest
import torch
import numpy as np

from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


class Test(unittest.TestCase):
    def test_framework_pytorch(self):

        model = torch.nn.Sequential(
            torch.nn.Linear(20, 20),
            torch.nn.ReLU(),
            torch.nn.Linear(20, 8),
            torch.nn.ReLU(),
            torch.nn.Linear(8, 2),
            torch.nn.LogSoftmax(),
        ).double()

        loss_fn = torch.nn.NLLLoss()

        learning_rate = 1e-3
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        X, y = make_classification(n_samples=100000, n_features=20, n_classes=2, random_state=42)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

        X_train = torch.tensor(X_train, dtype=torch.double)
        X_test = torch.tensor(X_test, dtype=torch.double)

        y_train = torch.tensor(y_train, dtype=torch.long)
        y_test = torch.tensor(y_test, dtype=torch.long)

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

        y_pred = model(X_test)
        model_loss = loss_fn(y_pred, y_test).item()

        torch.save(model.state_dict(), "model.pt")

        loaded_model = torch.nn.Sequential(
            torch.nn.Linear(20, 20),
            torch.nn.ReLU(),
            torch.nn.Linear(20, 8),
            torch.nn.ReLU(),
            torch.nn.Linear(8, 2),
            torch.nn.LogSoftmax(),
        ).double()
        loaded_model.load_state_dict(torch.load("model.pt"))
        loaded_model.eval()

        y_pred = loaded_model(X_test)
        loaded_model_loss = loss_fn(y_pred, y_test).item()

        self.assertEqual(loaded_model_loss, model_loss)


if __name__ == "__main__":

    unittest.main(verbosity=2)
