import tempfile,unittest
from pathlib import Path
from maestro.fabric import FabricDatabase,DistributedLockManager
class T(unittest.TestCase):
 def test_lock_ownership(self):
  with tempfile.TemporaryDirectory() as td:
   m=DistributedLockManager(FabricDatabase(Path(td)/'f.db')); a=m.acquire('task:T1','node1',30); self.assertIsNotNone(a); self.assertIsNone(m.acquire('task:T1','node2',30)); m.release(a.lock_name,a.owner_id,a.token); self.assertIsNotNone(m.acquire('task:T1','node2',30))
if __name__=='__main__': unittest.main()
