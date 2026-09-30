from __future__ import annotations
from dataclasses import dataclass,field,asdict
from datetime import datetime,timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

def now(): return datetime.now(timezone.utc).isoformat()
class OutcomeStatus(StrEnum): SUCCESS='SUCCESS'; PARTIAL='PARTIAL'; FAILURE='FAILURE'; ABORTED='ABORTED'; UNKNOWN='UNKNOWN'
class LearningStatus(StrEnum): OBSERVED='OBSERVED'; CANDIDATE='CANDIDATE'; EVALUATING='EVALUATING'; SHADOW='SHADOW'; APPROVED='APPROVED'; REJECTED='REJECTED'; SUPERSEDED='SUPERSEDED'; EXPIRED='EXPIRED'
class LearningKind(StrEnum): FAILURE_PATTERN='FAILURE_PATTERN'; SUCCESS_PATTERN='SUCCESS_PATTERN'; ROUTING_POLICY='ROUTING_POLICY'; CONTEXT_POLICY='CONTEXT_POLICY'; TOOL_POLICY='TOOL_POLICY'; MODEL_POLICY='MODEL_POLICY'; SKILL='SKILL'; PRINCIPLE='PRINCIPLE'
@dataclass(slots=True)
class ExperienceRecord:
    task_id:str; task_family:str; councils:list[str]; strategies:list[str]; tool_names:list[str]; outcome:OutcomeStatus; verified:bool
    evidence_ids:list[str]=field(default_factory=list); faults:list[str]=field(default_factory=list); human_corrections:list[str]=field(default_factory=list)
    cost_units:float|None=None; latency_ms:float|None=None; metadata:dict[str,Any]=field(default_factory=dict); created_at:str=field(default_factory=now)
    experience_id:str=field(default_factory=lambda:f"EXP-{uuid4().hex[:12].upper()}")
    def to_dict(self):
        d=asdict(self); d['outcome']=self.outcome.value; return d
@dataclass(slots=True)
class LearningCandidate:
    kind:LearningKind; key:str; statement:str; support_experience_ids:list[str]; counter_experience_ids:list[str]=field(default_factory=list)
    status:LearningStatus=LearningStatus.CANDIDATE; version:int=1; evaluation_score:float|None=None; rollback_to:str|None=None
    metadata:dict[str,Any]=field(default_factory=dict); created_at:str=field(default_factory=now); candidate_id:str=field(default_factory=lambda:f"LRN-{uuid4().hex[:12].upper()}")
    @property
    def support_count(self): return len(self.support_experience_ids)
    @property
    def counter_count(self): return len(self.counter_experience_ids)
