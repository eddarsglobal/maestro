import tempfile,unittest
from maestro.storage.object_store import BinaryObjectStore
from maestro.learning.experience_store import ExperienceStore
from maestro.learning.engine import LearningEngine
from maestro.learning.models import ExperienceRecord,OutcomeStatus,LearningStatus
from maestro.learning.promotion import PromotionGate,EvaluationResult,PromotionDenied
class T(unittest.TestCase):
 def engine(self,td): return LearningEngine(ExperienceStore(BinaryObjectStore(td)))
 def test_unverified_not_learned(self):
  with tempfile.TemporaryDirectory() as td:
   e=self.engine(td); e.ingest(ExperienceRecord('T','X',['IT'],['S'],[],OutcomeStatus.FAILURE,False,faults=['boom'])); self.assertEqual(len(e.failures.patterns),0)
 def test_three_verified_successes_distill(self):
  with tempfile.TemporaryDirectory() as td:
   e=self.engine(td)
   for i in range(3): e.ingest(ExperienceRecord(f'T{i}','WEBHOOK',['IT','SC'],['IDEMPOTENT'],[],OutcomeStatus.SUCCESS,True))
   self.assertEqual(len(e.distill_candidates()),1)
 def test_promotion_governed(self):
  with tempfile.TemporaryDirectory() as td:
   e=self.engine(td)
   for i in range(3): e.ingest(ExperienceRecord(f'T{i}','WEBHOOK',['IT'],['S'],[],OutcomeStatus.SUCCESS,True))
   c=e.ledger.candidates[e.distill_candidates()[0]]; r=EvaluationResult(.99,0,.99,100); g=PromotionGate()
   with self.assertRaises(PromotionDenied): g.evaluate(c,r,ay_validated=False,ex_authorized=True)
   self.assertTrue(g.evaluate(c,r,ay_validated=True,ex_authorized=True)); self.assertEqual(c.status,LearningStatus.APPROVED)
