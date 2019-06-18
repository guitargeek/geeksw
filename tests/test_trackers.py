import unittest
from geeksw.caching import make_f_hash_cache_tracker


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

    def test_make_f_hash_cache_tracker(self):

        tracker = make_f_hash_cache_tracker(strict=True, verbosity=1)

        @tracker.function
        def add_lastname(name):
            return name + " Doe"

        @tracker.function
        def say_hello(name):
            return "Hello " + name + "!"

        class Jon(object):
            name = "Jon Sno"

            @tracker.method
            def say_hello(self, name):
                return "Hello " + name + ", I'm " + self.name + "!"

        name = "Joe"

        say_hello(add_lastname(name))

        Jon().say_hello(add_lastname(name))


if __name__ == "__main__":

    unittest.main(verbosity=2)
