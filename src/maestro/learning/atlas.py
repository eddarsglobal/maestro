from __future__ import annotations
from dataclasses import dataclass,field
import hashlib
from .models import ExperienceRecord,OutcomeStatus

def fp(parts): return hashlib.sha256('|'.join(' '.join(x.lower().split()) for x in parts).encode()).hexdigest()[:20]
@dataclass(slots=True)
class PatternStats:
    fingerprint:str; support_experience_ids:list[str]=field(default_factory=list); counter_experience_ids:list[str]=field(default_factory=list); metadata:dict=field(default_factory=dict)
    @property
    def support(self): return len(self.support_experience_ids)
class FailureAtlas:
    def __init__(self): self.patterns={}
    def observe(self,e:ExperienceRecord):
        if not e.verified:return
        for fault in e.faults:
            k=fp([e.task_family,fault]); p=self.patterns.setdefault(k,PatternStats(k,metadata={'task_family':e.task_family,'fault':fault}))
            (p.support_experience_ids if e.outcome is OutcomeStatus.FAILURE else p.counter_experience_ids).append(e.experience_id)
class SuccessAtlas:
    def __init__(self): self.patterns={}
    def observe(self,e:ExperienceRecord):
        if not e.verified or e.outcome is not OutcomeStatus.SUCCESS:return
        k=fp([e.task_family,','.join(sorted(e.councils)),','.join(e.strategies)]); p=self.patterns.setdefault(k,PatternStats(k,metadata={'task_family':e.task_family,'councils':sorted(e.councils),'strategies':list(e.strategies)})); p.support_experience_ids.append(e.experience_id)
