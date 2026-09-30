import tempfile,unittest
from maestro.resilience.cluster import ResilientCluster
from maestro.fabric.workers import WorkerAdvertisement
from maestro.resilience.placement_learning import PlacementObservation
class T(unittest.TestCase):
 def test_history_can_prefer_better_worker(self):
  with tempfile.TemporaryDirectory() as td:
   c=ResilientCluster(td)
   c.fabric.workers.advertise(WorkerAdvertisement('w1','n1',{'IT'},{'code'},load=0.1))
   c.fabric.workers.advertise(WorkerAdvertisement('w2','n2',{'IT'},{'code'},load=0.1))
   for _ in range(10):
    c.placement.observe(PlacementObservation('w1','n1','IT',False,1000,5))
    c.placement.observe(PlacementObservation('w2','n2','IT',True,100,1))
   d=c.placement.place('IT',{'code'}); self.assertEqual(d.worker_id,'w2')
if __name__=='__main__': unittest.main()
