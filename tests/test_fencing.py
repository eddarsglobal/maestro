import tempfile,unittest,time
from maestro.fabric.sqlite_backend import FabricDatabase
from maestro.resilience.backend import SQLiteClusterBackend
from maestro.resilience.fencing import FencedLockManager,StaleFencingToken
class T(unittest.TestCase):
 def test_tokens_monotonic_and_old_stale(self):
  with tempfile.TemporaryDirectory() as td:
   m=FencedLockManager(SQLiteClusterBackend(FabricDatabase(f'{td}/f.db')))
   a=m.acquire('db','A',ttl_seconds=1); self.assertIsNotNone(a)
   # force expiry then reacquire
   with m.backend.immediate() as con: con.execute('UPDATE cluster_fenced_locks SET expires_at=? WHERE lock_name=?',(time.time()-1,'db'))
   b=m.acquire('db','B',ttl_seconds=30)
   self.assertGreater(b.fencing_token,a.fencing_token)
   with self.assertRaises(StaleFencingToken): m.heartbeat(a)
if __name__=='__main__': unittest.main()
