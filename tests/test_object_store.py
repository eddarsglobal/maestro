import tempfile,unittest
from maestro.storage.object_store import BinaryObjectStore
class T(unittest.TestCase):
 def test_dedup(self):
  with tempfile.TemporaryDirectory() as td:
   s=BinaryObjectStore(td); a=s.put(1,{'x':1}); b=s.put(1,{'x':1})
   self.assertEqual(a.sha256,b.sha256); self.assertEqual(s.object_count(),1); self.assertEqual(s.get(a),{'x':1})
