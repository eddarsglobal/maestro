import tempfile,unittest
from pathlib import Path
from maestro.storage.object_store import BinaryObjectStore
from maestro.fabric import FabricDatabase,AcademyBatchIngestor
class T(unittest.TestCase):
 def test_batch(self):
  with tempfile.TemporaryDirectory() as td:
   a=AcademyBatchIngestor(FabricDatabase(Path(td)/'f.db'),BinaryObjectStore(Path(td)/'obj')); ref=a.ingest([{'s':1}],[{'x':2}]); self.assertEqual(ref.items,2); self.assertEqual(len(a.pending()),1); payload=a.consume(ref.batch_id); self.assertEqual(payload['scenario_results'][0]['s'],1); self.assertEqual(len(a.pending()),0)
if __name__=='__main__': unittest.main()
