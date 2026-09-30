import tempfile
import unittest

from maestro.os.operating_system import MaestroOperatingSystem


class MaestroOSTests(unittest.TestCase):
    def test_composition_root(self):
        with tempfile.TemporaryDirectory() as td:
            osys = MaestroOperatingSystem(td)
            self.assertIsNotNone(osys.runtime)
            self.assertIsNotNone(osys.leases)
            self.assertIsNotNone(osys.op)
            self.assertIsNotNone(osys.event_sourcing)


if __name__ == "__main__":
    unittest.main()
