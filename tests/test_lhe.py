import unittest
import os

from geeksw.lhe import LHEReader

data_dir = "tests/lhe_data"

data1 = os.path.join(data_dir, "zzz_ft9_3_events.lhe")
data2 = os.path.join(data_dir, "zzz_ft9_0_events.lhe")

n_events = {data1: 3, data2: 0}

n_particles_per_event = 11  # We know this from how the data was generated and can use it to validate


class TestLHE(unittest.TestCase):
    def _test_lhe_simple(self, data, maxevents, batch_size=None):
        lhe_reader = LHEReader(data, maxevents=maxevents, batch_size=batch_size)

        particles = lhe_reader.particle_data_frame()
        event_data = lhe_reader.event_data_frame()
        weights = lhe_reader.reweighting_data_frame()

        expected_events = n_events[data]
        if not maxevents is None:
            expected_events = min(maxevents, expected_events)

        assert len(weights) == expected_events
        assert len(event_data) == expected_events
        assert len(particles) == expected_events * n_particles_per_event

        assert len(event_data.columns) == 6
        assert len(particles.columns) == 14

    def test_lhe_1(self):
        self._test_lhe_simple(data1, 2, None)
        self._test_lhe_simple(data1, 3, None)
        self._test_lhe_simple(data1, 4, None)
        self._test_lhe_simple(data1, None, None)

    def test_lhe_2(self):
        self._test_lhe_simple(data1, 2, 2)
        self._test_lhe_simple(data1, 3, 2)
        self._test_lhe_simple(data1, 4, 2)
        self._test_lhe_simple(data1, None, 2)

    def test_lhe_3(self):
        self._test_lhe_simple(data2, 0, None)
        self._test_lhe_simple(data2, 1, None)
        self._test_lhe_simple(data2, None, None)
        self._test_lhe_simple(data2, 0, 2)
        self._test_lhe_simple(data2, 1, 2)
        self._test_lhe_simple(data2, None, 2)


if __name__ == "__main__":

    unittest.main(verbosity=2)
