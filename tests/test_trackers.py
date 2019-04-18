import unittest
from geeksw.caching import FHashCacheTracker


class Test(unittest.TestCase):
    def test_dummy_tracker(self):

        tracker = lambda x: x

        @tracker
        def add_lastname(name):
            return name + " Doe"

        @tracker
        def say_hello(name):
            return "Hello " + name + "!!"

        name = "Joe"

        say_hello(add_lastname(name))

    def test_FHashCacheTracker(self):

        tracker = FHashCacheTracker(strict=True, verbosity=1)

        @tracker
        def add_lastname(name):
            return name + " Doe"

        @tracker
        def say_hello(name):
            return "Hello " + name + "!!"

        name = "Joe"

        say_hello(add_lastname(name))


if __name__ == "__main__":

    unittest.main(verbosity=2)
