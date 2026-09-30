import tempfile,unittest
from maestro.fabric.sqlite_backend import FabricDatabase
from maestro.fabric.workers import WorkerDirectory,WorkerAdvertisement
from maestro.resilience.backend import SQLiteClusterBackend
from maestro.resilience.nodes import NodeDirectory,NodeRecord
from maestro.resilience.chaos import ChaosHarness
class T(unittest.TestCase):
 def test_node_failure_marks_worker_offline(self):
  with tempfile.TemporaryDirectory() as td:
   db=FabricDatabase(f'{td}/f.db'); b=SQLiteClusterBackend(db); nd=NodeDirectory(b); wd=WorkerDirectory(db)
   nd.advertise(NodeRecord('n1')); wd.advertise(WorkerAdvertisement('w1','n1',{'IT'},{'code'}))
   ChaosHarness(b).fail_node('n1')
   self.assertEqual(nd.live(),[]); self.assertEqual(wd.discover('IT',{'code'}),[])
if __name__=='__main__': unittest.main()
