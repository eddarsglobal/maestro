import tempfile,unittest
from pathlib import Path
from maestro import MaestroKernel
from maestro.storage.object_store import BinaryObjectStore
from maestro.fabric import FabricDatabase,CrossNodeCheckpointStore
class T(unittest.TestCase):
 def test_cross_node_checkpoint(self):
  with tempfile.TemporaryDirectory() as td:
   k=MaestroKernel(); m=k.create_mission('x'); s=CrossNodeCheckpointStore(FabricDatabase(Path(td)/'f.db'),BinaryObjectStore(Path(td)/'obj'))
   s.save(m.task_id,m.to_dict(),k.dag(m).snapshot(),k.retry_ledgers[m.task_id].snapshot(),'NODE-A'); b=s.load(m.task_id); self.assertEqual(b.mission.task_id,m.task_id); self.assertEqual(b.source_node,'NODE-A'); self.assertEqual(b.generation,1)
if __name__=='__main__': unittest.main()
