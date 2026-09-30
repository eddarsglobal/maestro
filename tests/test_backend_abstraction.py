import tempfile,unittest
from maestro.fabric.sqlite_backend import FabricDatabase
from maestro.resilience.backend import SQLiteClusterBackend
class T(unittest.TestCase):
 def test_backend(self):
  with tempfile.TemporaryDirectory() as td:
   b=SQLiteClusterBackend(FabricDatabase(f'{td}/f.db'))
   with b.connect() as con: self.assertEqual(con.execute('SELECT 1').fetchone()[0],1)
if __name__=='__main__': unittest.main()
