import tempfile,unittest
from pathlib import Path
from maestro.governance.mass_budget import LightnessGovernor,MassBudget,MassBudgetExceeded
class T(unittest.TestCase):
 def test_pass(self):
  with tempfile.TemporaryDirectory() as td:
   Path(td,'x').write_text('hi'); g=LightnessGovernor(MassBudget(1000,0,1000,10)); s=g.audit(core_path=td,loaded_dynamic_councils=0,context_bytes=100,working_evidence_items=2,idle=True); self.assertLess(s.core_disk_bytes,1000)
 def test_idle_residency_block(self):
  with tempfile.TemporaryDirectory() as td:
   g=LightnessGovernor(MassBudget(1000,0,1000,10))
   with self.assertRaises(MassBudgetExceeded): g.audit(core_path=td,loaded_dynamic_councils=1,context_bytes=100,working_evidence_items=1,idle=True)
