import tempfile,unittest
from pathlib import Path
from maestro.fabric import FabricDatabase,IdempotencyStore,IdempotencyConflict
class T(unittest.TestCase):
 def test_idempotency(self):
  with tempfile.TemporaryDirectory() as td:
   s=IdempotencyStore(FabricDatabase(Path(td)/'f.db'))
   self.assertTrue(s.begin('K',{'x':1})); self.assertFalse(s.begin('K',{'x':1}))
   with self.assertRaises(IdempotencyConflict): s.begin('K',{'x':2})
   s.complete('K',{'ok':True}); self.assertTrue(s.result('K')['ok'])
if __name__=='__main__': unittest.main()
