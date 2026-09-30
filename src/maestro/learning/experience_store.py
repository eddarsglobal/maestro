from __future__ import annotations
from maestro.storage.object_store import BinaryObjectStore,ObjectRef
from .models import ExperienceRecord,OutcomeStatus
EXPERIENCE_OBJECT_TYPE=0x21
class ExperienceStore:
    def __init__(self,objects:BinaryObjectStore): self.objects=objects; self._index:dict[str,ObjectRef]={}
    def add(self,exp:ExperienceRecord)->str:
        if exp.experience_id in self._index: raise ValueError('duplicate experience')
        self._index[exp.experience_id]=self.objects.put(EXPERIENCE_OBJECT_TYPE,exp.to_dict()); return exp.experience_id
    def get(self,eid:str)->ExperienceRecord:
        r=self.objects.get(self._index[eid]); return ExperienceRecord(task_id=r['task_id'],task_family=r['task_family'],councils=list(r['councils']),strategies=list(r['strategies']),tool_names=list(r['tool_names']),outcome=OutcomeStatus(r['outcome']),verified=bool(r['verified']),evidence_ids=list(r.get('evidence_ids',[])),faults=list(r.get('faults',[])),human_corrections=list(r.get('human_corrections',[])),cost_units=r.get('cost_units'),latency_ms=r.get('latency_ms'),metadata=dict(r.get('metadata',{})),created_at=r['created_at'],experience_id=r['experience_id'])
    def ids(self): return sorted(self._index)
