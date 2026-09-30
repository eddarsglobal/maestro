import tempfile,time,unittest
from pathlib import Path
from maestro.fabric import FabricDatabase,PersistentWorkQueue,FabricWorkItem,FabricWorkStatus
class T(unittest.TestCase):
 def test_persist_lease_reclaim(self):
  with tempfile.TemporaryDirectory() as td:
   q=PersistentWorkQueue(FabricDatabase(Path(td)/'f.db')); wid=q.enqueue(FabricWorkItem('T1','IT','CODE',idempotency_key='k1'))
   self.assertEqual(q.enqueue(FabricWorkItem('T1','IT','CODE',idempotency_key='k1')),wid)
   x=q.lease_next('W1',{'IT'},lease_seconds=0); self.assertEqual(x.status,FabricWorkStatus.LEASED)
   self.assertEqual(q.reclaim_expired(),[wid]); self.assertEqual(q.get(wid).status,FabricWorkStatus.QUEUED)
if __name__=='__main__': unittest.main()
