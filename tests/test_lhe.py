import unittest
import os

from geeksw.lhe import LHEReader

data_dir = "tests/lhe_data"

data_1 = os.path.join(data_dir, "zzz_ft9_3_events.lhe")

n_particles_per_event = 11  # We know this from how the data was generated and can use it to validate


class TestLHE(unittest.TestCase):
    def _test_lhe_maxevents(self, maxevents):
        lhe_reader = LHEReader(data_1, maxevents=maxevents, batch_size=None)

        particles = lhe_reader.particle_data_frame()
        event_data = lhe_reader.event_data_frame()
        weights = lhe_reader.reweighting_data_frame()

        if maxevents is None:
            expected_events = 3
        else:
            expected_events = min(maxevents, 3)

        assert len(weights) == expected_events
        assert len(event_data) == expected_events
        assert len(particles) == expected_events * n_particles_per_event

    def test_lhe_1(self):
        """Test if no maxevents is set.
        """
        self._test_lhe_maxevents(None)

    def test_lhe_2(self):
        """Test if maxevents is smaller than the number of events.
        """
        self._test_lhe_maxevents(2)

    def test_lhe_3(self):
        """Test if maxevents is equal the number of events.
        """
        self._test_lhe_maxevents(3)

    def test_lhe_4(self):
        """Test if maxevents is larger than the number of events.
        """
        self._test_lhe_maxevents(4)


if __name__ == "__main__":

    unittest.main(verbosity=2)
