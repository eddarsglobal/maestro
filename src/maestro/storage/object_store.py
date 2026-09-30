from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import hashlib
from .mobj import Mobj,encode,decode

@dataclass(frozen=True,slots=True)
class ObjectRef:
    sha256:str
    object_type:int
    stored_bytes:int

class BinaryObjectStore:
    def __init__(self,root:str|Path):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def _path(self,sha:str)->Path: return self.root/sha[:2]/sha[2:4]/f"{sha}.mobj"
    def put(self,object_type:int,payload:dict[str,Any])->ObjectRef:
        blob=encode(Mobj(object_type,payload,True)); sha=hashlib.sha256(blob).hexdigest(); p=self._path(sha)
        if not p.exists(): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(blob)
        return ObjectRef(sha,object_type,len(blob))
    def get(self,ref:ObjectRef|str)->dict[str,Any]:
        sha=ref.sha256 if isinstance(ref,ObjectRef) else ref; p=self._path(sha)
        if not p.exists(): raise KeyError(sha)
        return decode(p.read_bytes()).payload
    def object_count(self)->int: return sum(1 for _ in self.root.rglob('*.mobj'))
    def physical_bytes(self)->int: return sum(p.stat().st_size for p in self.root.rglob('*.mobj'))
