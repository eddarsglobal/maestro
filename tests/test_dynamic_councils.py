import tempfile,unittest
from maestro.storage.object_store import BinaryObjectStore
from maestro.councils.capsules import CouncilCapsuleStore,CouncilCapsuleManifest
from maestro.councils.dynamic_registry import DynamicCouncilRegistry,CouncilInstallDenied
from maestro.councils.gap_detector import CapabilityGapDetector
class T(unittest.TestCase):
 def reg(self,td): return DynamicCouncilRegistry(CouncilCapsuleStore(BinaryObjectStore(td)))
 def test_genesis_18(self):
  with tempfile.TemporaryDirectory() as td: self.assertEqual(len(self.reg(td).genesis_ids),18)
 def test_cannot_replace_genesis(self):
  with tempfile.TemporaryDirectory() as td:
   r=self.reg(td); m=CouncilCapsuleManifest('IT','Fake','$conseil-it','fake',['fake'],[],[])
   with self.assertRaises(CouncilInstallDenied): r.propose(m)
 def test_install_governed(self):
  with tempfile.TemporaryDirectory() as td:
   r=self.reg(td); m=CouncilCapsuleManifest('RB','Robotics','$conseil-rb','robotics safety',['robotics_safety'],['robot'],['final system verdict']); r.propose(m)
   with self.assertRaises(CouncilInstallDenied): r.install('RB',eval_passed=True,ay_validated=True,ex_authorized=True,human_approved=True)
   r.promote_to_shadow('RB',ay_validated=True)
   with self.assertRaises(CouncilInstallDenied): r.install('RB',eval_passed=True,ay_validated=True,ex_authorized=True,human_approved=False)
   r.install('RB',eval_passed=True,ay_validated=True,ex_authorized=True,human_approved=True); self.assertEqual(r.installed_dynamic(),['RB'])
 def test_gap_detector(self):
  with tempfile.TemporaryDirectory() as td:
   r=self.reg(td); d=CapabilityGapDetector(r); g=d.detect(['orbital_safety_certification']); self.assertTrue(g.gap_exists)
