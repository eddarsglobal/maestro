import tempfile,unittest
from maestro.resilience.cluster import ResilientCluster
from maestro.fabric.queue import FabricWorkItem
from maestro.resilience.nodes import NodeRecord
class T(unittest.TestCase):
 def test_snapshot(self):
  with tempfile.TemporaryDirectory() as td:
   c=ResilientCluster(td); c.nodes.advertise(NodeRecord('n1')); c.fabric.queue.enqueue(FabricWorkItem('T','IT','CODE'))
   s=c.observability.snapshot(); self.assertEqual(s.queued,1); self.assertEqual(s.live_nodes,1)
if __name__=='__main__': unittest.main()
