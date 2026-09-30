import unittest
from maestro.meta_cognition import ConfidenceCalibrationLedger

class MetaCalibrationTests(unittest.TestCase):
    def test_detects_overconfidence(self):
        l=ConfidenceCalibrationLedger()
        l.record(0.95,True,0.4)
        l.record(0.9,False,0.0)
        self.assertGreater(l.overconfidence_rate(),0.5)
        self.assertIsNotNone(l.calibration_error())

if __name__=="__main__":
    unittest.main()
