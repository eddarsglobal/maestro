from __future__ import annotations
from dataclasses import dataclass,field,asdict
from enum import StrEnum
from typing import Any
import re
from maestro.storage.object_store import BinaryObjectStore,ObjectRef
CAPSULE_OBJECT_TYPE=0x31; ID_RE=re.compile(r'^[A-Z][A-Z0-9_]{1,15}$')
class CapsuleStatus(StrEnum): PROPOSED='PROPOSED'; SHADOW='SHADOW'; APPROVED='APPROVED'; INSTALLED='INSTALLED'; DEPRECATED='DEPRECATED'
@dataclass(slots=True)
class CouncilCapsuleManifest:
    council_id:str; name:str; system_variable:str; primary_authority:str; capabilities:list[str]; triggers:list[str]; cannot_own:list[str]; version:str='0.1.0'; status:CapsuleStatus=CapsuleStatus.PROPOSED; genesis:bool=False; metadata:dict[str,Any]=field(default_factory=dict)
    def validate(self):
        if not ID_RE.match(self.council_id): raise ValueError('invalid council_id')
        if self.system_variable!=f'$conseil-{self.council_id.lower()}': raise ValueError('system variable mismatch')
        if not self.capabilities or not self.primary_authority.strip(): raise ValueError('authority/capabilities required')
    def to_dict(self): d=asdict(self); d['status']=self.status.value; return d
class CouncilCapsuleStore:
    def __init__(self,objects:BinaryObjectStore): self.objects=objects; self.refs:dict[str,ObjectRef]={}; self.cache={}
    def store(self,m:CouncilCapsuleManifest): m.validate(); self.refs[m.council_id]=self.objects.put(CAPSULE_OBJECT_TYPE,m.to_dict()); self.cache.pop(m.council_id,None)
    def load(self,cid:str):
        if cid in self.cache:return self.cache[cid]
        r=self.objects.get(self.refs[cid]); m=CouncilCapsuleManifest(r['council_id'],r['name'],r['system_variable'],r['primary_authority'],list(r['capabilities']),list(r.get('triggers',[])),list(r.get('cannot_own',[])),r.get('version','0.1.0'),CapsuleStatus(r['status']),bool(r.get('genesis',False)),dict(r.get('metadata',{}))); m.validate(); self.cache[cid]=m; return m
    def unload(self,cid:str): self.cache.pop(cid,None)
    def loaded_count(self): return len(self.cache)
    def ids(self): return sorted(self.refs)
