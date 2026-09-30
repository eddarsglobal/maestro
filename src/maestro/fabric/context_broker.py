from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from maestro.storage.object_store import BinaryObjectStore,ObjectRef

CONTEXT_OBJECT_TYPE=0x61
@dataclass(frozen=True,slots=True)
class ContextRef:
    sha256:str; bytes:int

class ContextBroker:
    def __init__(self,objects:BinaryObjectStore): self.objects=objects
    def publish(self,context:dict[str,Any])->ContextRef:
        ref=self.objects.put(CONTEXT_OBJECT_TYPE,context); return ContextRef(ref.sha256,ref.stored_bytes)
    def hydrate(self,ref:ContextRef|str)->dict[str,Any]: return self.objects.get(ref.sha256 if isinstance(ref,ContextRef) else ref)
