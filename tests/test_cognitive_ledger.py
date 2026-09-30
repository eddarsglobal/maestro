import tempfile
import unittest
from pathlib import Path
from maestro.cognitive_fabric import *

class LedgerTests(unittest.TestCase):
    def test_compact_record(self):
        with tempfile.TemporaryDirectory() as td:
            l=CognitiveFabricLedger(Path(td)/"cog.jsonl")
            a=StageArtifact("s",CognitiveRole.PRODUCER,"r","p","m","hello",True,0.8)
            l.record_artifact("T",a)
            self.assertEqual(l.rows[0]["output_chars"],5)
            self.assertNotIn("thinking",l.rows[0])

if __name__=="__main__":
    unittest.main()
