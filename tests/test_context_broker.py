import tempfile,unittest
from maestro.storage.object_store import BinaryObjectStore
from maestro.fabric import ContextBroker
class T(unittest.TestCase):
 def test_context_reference_dedup(self):
  with tempfile.TemporaryDirectory() as td:
   b=ContextBroker(BinaryObjectStore(td)); a=b.publish({'x':'y'*100}); c=b.publish({'x':'y'*100}); self.assertEqual(a.sha256,c.sha256); self.assertEqual(b.hydrate(a)['x'],'y'*100)
if __name__=='__main__': unittest.main()
