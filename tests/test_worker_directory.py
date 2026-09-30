import tempfile,unittest
from pathlib import Path
from maestro.fabric import FabricDatabase,WorkerDirectory,WorkerAdvertisement,CouncilPlacementStrategy
class T(unittest.TestCase):
 def test_discovery_and_placement(self):
  with tempfile.TemporaryDirectory() as td:
   d=WorkerDirectory(FabricDatabase(Path(td)/'f.db')); d.advertise(WorkerAdvertisement('W1','N1',{'IT'},{'python'},0.7)); d.advertise(WorkerAdvertisement('W2','N2',{'IT'},{'python','gpu'},0.1))
   x=d.discover('IT',{'python'}); self.assertEqual(x[0].worker_id,'W2'); p=CouncilPlacementStrategy(d).place('IT',{'python'},preferred_node='N1'); self.assertIn(p.worker_id,{'W1','W2'})
if __name__=='__main__': unittest.main()
