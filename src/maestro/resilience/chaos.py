from __future__ import annotations
from dataclasses import dataclass,asdict
import json,time
from .backend import ClusterBackend

@dataclass(frozen=True,slots=True)
class ChaosEvent:
    event_type:str; target:str; payload:dict

class ChaosHarness:
    """Deterministic failure injection for tests/staging. Never enabled implicitly in production."""
    def __init__(self,backend:ClusterBackend): self.backend=backend
    def _record(self,event:ChaosEvent):
        with self.backend.immediate() as con:
            con.execute('INSERT INTO cluster_chaos_events(event_type,target,payload_json,created_at) VALUES(?,?,?,?)',(event.event_type,event.target,json.dumps(event.payload,sort_keys=True),time.time()))
    def expire_worker(self,worker_id:str,seconds:int=3600)->ChaosEvent:
        with self.backend.immediate() as con: con.execute('UPDATE fabric_workers SET last_heartbeat=last_heartbeat-? WHERE worker_id=?',(seconds,worker_id))
        e=ChaosEvent('EXPIRE_WORKER',worker_id,{'seconds':seconds}); self._record(e); return e
    def expire_work_lease(self,work_id:str,seconds:int=3600)->ChaosEvent:
        with self.backend.immediate() as con: con.execute('UPDATE fabric_work SET lease_expires=lease_expires-? WHERE work_id=?',(seconds,work_id))
        e=ChaosEvent('EXPIRE_WORK_LEASE',work_id,{'seconds':seconds}); self._record(e); return e
    def fail_node(self,node_id:str)->ChaosEvent:
        with self.backend.immediate() as con:
            con.execute('UPDATE cluster_nodes SET state=? WHERE node_id=?',('FAILED',node_id))
            con.execute('UPDATE fabric_workers SET state=? WHERE node_id=?',('OFFLINE',node_id))
        e=ChaosEvent('FAIL_NODE',node_id,{}); self._record(e); return e
