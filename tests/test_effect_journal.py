import tempfile,unittest
from maestro.fabric.sqlite_backend import FabricDatabase
from maestro.resilience.backend import SQLiteClusterBackend
from maestro.resilience.effects import EffectJournal,EffectConflict,EffectState
class T(unittest.TestCase):
 def test_idempotent_prepare_commit(self):
  with tempfile.TemporaryDirectory() as td:
   j=EffectJournal(SQLiteClusterBackend(FabricDatabase(f'{td}/f.db')))
   r,new=j.prepare('send-1',{'to':'a'},7); self.assertTrue(new)
   r2,new2=j.prepare('send-1',{'to':'a'},7); self.assertFalse(new2)
   out=j.commit('send-1',{'sent':True},7); self.assertEqual(out.state,EffectState.COMMITTED)
   self.assertEqual(j.commit('send-1',{'sent':True},7).result,{'sent':True})
   with self.assertRaises(EffectConflict): j.prepare('send-1',{'to':'b'},7)
if __name__=='__main__': unittest.main()
