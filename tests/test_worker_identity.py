import tempfile,unittest
from maestro.fabric.sqlite_backend import FabricDatabase
from maestro.resilience.backend import SQLiteClusterBackend
from maestro.resilience.identity import WorkerIdentityAuthority,IdentityError
class T(unittest.TestCase):
 def test_challenge_response_and_replay_block(self):
  with tempfile.TemporaryDirectory() as td:
   a=WorkerIdentityAuthority(SQLiteClusterBackend(FabricDatabase(f'{td}/f.db')))
   secret=a.enroll('w1',b'x'*32); c=a.issue_challenge('w1'); sig=a.sign(secret,c)
   self.assertTrue(a.verify(c,sig))
   with self.assertRaises(IdentityError): a.verify(c,sig)
if __name__=='__main__': unittest.main()
