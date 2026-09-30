import tempfile,unittest
from maestro.fabric import DistributedIntelligenceFabric
class T(unittest.TestCase):
 def test_composition(self):
  with tempfile.TemporaryDirectory() as td:
   f=DistributedIntelligenceFabric(td); self.assertIsNotNone(f.queue); self.assertIsNotNone(f.placement); self.assertIsNotNone(f.contexts)
if __name__=='__main__': unittest.main()
