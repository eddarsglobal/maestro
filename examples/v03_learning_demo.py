import tempfile
from pathlib import Path
from maestro.storage.object_store import BinaryObjectStore
from maestro.learning.experience_store import ExperienceStore
from maestro.learning.engine import LearningEngine
from maestro.learning.models import ExperienceRecord,OutcomeStatus
from maestro.councils.capsules import CouncilCapsuleStore
from maestro.councils.dynamic_registry import DynamicCouncilRegistry
from maestro.councils.gap_detector import CapabilityGapDetector
from maestro.governance.mass_budget import LightnessGovernor,MassBudget
with tempfile.TemporaryDirectory() as td:
 td=Path(td); objects=BinaryObjectStore(td/'objects'); learning=LearningEngine(ExperienceStore(objects))
 for i in range(3): learning.ingest(ExperienceRecord(f'TASK-{i}','PAYMENT_WEBHOOK',['PM','IT','SC','OP','AY'],['IDEMPOTENT_HANDLER'],['integration_test'],OutcomeStatus.SUCCESS,True,evidence_ids=[f'EVD-{i}']))
 print('LEARNING CANDIDATES:',learning.distill_candidates())
 caps=CouncilCapsuleStore(objects); reg=DynamicCouncilRegistry(caps); detector=CapabilityGapDetector(reg); gap=detector.detect(['orbital_safety_certification']); print('CAPABILITY GAP:',sorted(gap.missing))
 if gap.gap_exists:
  m=detector.propose_manifest(council_id='OS',name='Orbital Safety',authority='orbital safety governance',missing_capabilities=gap.missing,triggers=['spacecraft'],cannot_own=['final system verdict']); reg.propose(m); reg.promote_to_shadow('OS',ay_validated=True); reg.install('OS',eval_passed=True,ay_validated=True,ex_authorized=True,human_approved=True)
 print('DYNAMIC INSTALLED:',reg.installed_dynamic())
 before=objects.object_count(); a=objects.put(0x7F,{'same':'payload'}); b=objects.put(0x7F,{'same':'payload'}); print('DEDUP:',a.sha256==b.sha256,'OBJECT DELTA:',objects.object_count()-before)
 caps.unload('OS'); gov=LightnessGovernor(MassBudget(20_000_000,0,32768,256)); snap=gov.audit(core_path=Path(__file__).parents[1]/'src'/'maestro',loaded_dynamic_councils=caps.loaded_count(),context_bytes=2048,working_evidence_items=3,idle=True); print('MASS:',snap.to_dict())
