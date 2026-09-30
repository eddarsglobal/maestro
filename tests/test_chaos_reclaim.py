import tempfile,unittest
from maestro.resilience.cluster import ResilientCluster
from maestro.fabric.queue import FabricWorkItem,FabricWorkStatus
from maestro.fabric.workers import WorkerAdvertisement
class T(unittest.TestCase):
 def test_expired_lease_reclaimed(self):
  with tempfile.TemporaryDirectory() as td:
   c=ResilientCluster(td); c.fabric.workers.advertise(WorkerAdvertisement('w1','n1',{'IT'},{'code'}))
   wid=c.fabric.queue.enqueue(FabricWorkItem('T','IT','CODE'))
   item=c.fabric.queue.lease_next('w1',{'IT'},lease_seconds=30); c.chaos.expire_work_lease(item.work_id)
   ids=c.fabric.queue.reclaim_expired(); self.assertIn(item.work_id,ids); self.assertEqual(c.fabric.queue.get(item.work_id).status,FabricWorkStatus.QUEUED)
if __name__=='__main__': unittest.main()
