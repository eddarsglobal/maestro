import tempfile
import unittest
from pathlib import Path

from maestro.intelligence_market import IntelligenceMarketLedger, MarketObservation

class MarketLedgerTests(unittest.TestCase):
    def test_record_query_and_reload(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"market.jsonl"
            l = IntelligenceMarketLedger(path)
            l.record(MarketObservation("r1","CODE","IT",True,0.9,latency_ms=100))
            l.record(MarketObservation("r2","CODE","IT",False,0.2,latency_ms=200))
            self.assertEqual(len(l.query(task_family="CODE", council_id="IT")),2)
            l2 = IntelligenceMarketLedger(path)
            l2.load()
            self.assertEqual(len(l2.all()),2)

if __name__ == "__main__":
    unittest.main()
