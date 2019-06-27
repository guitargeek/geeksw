import unittest

from geeksw.functools import *


class Test(unittest.TestCase):
    def test_functools(self):
        l = ["ABC", "BSD", "ATS", "SAL", "CAB", "MDA", "SUF"]

        sel = set(filteranymap(contains, ["A"], l))

        for s in l:
            if s in sel:
                assert "A" in s
            else:
                assert not "A" in s

        sel = set(filteranymap(contains, ["A", "S"], l))

        for s in l:
            if s in sel:
                assert "A" in s or "S" in s
            else:
                assert not "A" in s and not "S" in s

        sel = set(filterallmap(contains, ["A"], l))

        for s in l:
            if s in sel:
                assert "A" in s
            else:
                assert not "A" in s

        sel = set(filterallmap(contains, ["A", "S"], l))

        for s in l:
            if s in sel:
                assert "A" in s and "S" in s
            else:
                assert not "A" in s or not "S" in s


if __name__ == "__main__":

    unittest.main(verbosity=2)
