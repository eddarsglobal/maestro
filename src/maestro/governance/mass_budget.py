from dataclasses import dataclass,asdict
from pathlib import Path
class MassBudgetExceeded(RuntimeError): pass
@dataclass(frozen=True,slots=True)
class MassBudget:
    max_core_disk_bytes:int; max_idle_loaded_councils:int=0; max_context_bytes_per_council:int=32768; max_working_evidence_items:int=256
@dataclass(slots=True)
class MassSnapshot:
    core_disk_bytes:int; loaded_dynamic_councils:int; context_bytes:int; working_evidence_items:int
    def to_dict(self): return asdict(self)
class LightnessGovernor:
    def __init__(self,budget): self.budget=budget
    @staticmethod
    def directory_bytes(path): return sum(p.stat().st_size for p in Path(path).rglob('*') if p.is_file())
    def audit(self,*,core_path,loaded_dynamic_councils,context_bytes,working_evidence_items,idle=False):
        s=MassSnapshot(self.directory_bytes(core_path),loaded_dynamic_councils,context_bytes,working_evidence_items)
        if s.core_disk_bytes>self.budget.max_core_disk_bytes: raise MassBudgetExceeded('core disk mass exceeded')
        if idle and s.loaded_dynamic_councils>self.budget.max_idle_loaded_councils: raise MassBudgetExceeded('idle Council residency exceeded')
        if s.context_bytes>self.budget.max_context_bytes_per_council: raise MassBudgetExceeded('context budget exceeded')
        if s.working_evidence_items>self.budget.max_working_evidence_items: raise MassBudgetExceeded('working evidence budget exceeded')
        return s
