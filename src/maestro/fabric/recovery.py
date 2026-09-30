from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import time
from maestro.storage.object_store import BinaryObjectStore
from maestro.runtime.checkpoint import _mission_from_dict
from maestro.orchestration.dag import DagEngine
from maestro.orchestration.retry_ledger import RetryLedger
from .sqlite_backend import FabricDatabase

CHECKPOINT_OBJECT_TYPE=0x62
@dataclass(slots=True)
class CrossNodeRecoveryBundle:
    mission:Any; dag:DagEngine; retry_ledger:RetryLedger; generation:int; source_node:str

class CrossNodeCheckpointStore:
    def __init__(self,db:FabricDatabase,objects:BinaryObjectStore): self.db=db; self.objects=objects
    def save(self,task_id:str,mission_dict:dict,dag_snapshot:dict,retry_snapshot:dict,node_id:str)->str:
        with self.db.immediate() as con:
            row=con.execute('SELECT generation FROM fabric_checkpoints WHERE task_id=?',(task_id,)).fetchone(); generation=(row['generation']+1) if row else 1
            payload={'task_id':task_id,'mission':mission_dict,'dag':dag_snapshot,'retry_ledger':retry_snapshot,'generation':generation,'node_id':node_id}
            ref=self.objects.put(CHECKPOINT_OBJECT_TYPE,payload)
            con.execute('INSERT OR REPLACE INTO fabric_checkpoints(task_id,object_hash,generation,node_id,created_at) VALUES(?,?,?,?,?)',(task_id,ref.sha256,generation,node_id,time.time()))
        return ref.sha256
    def load(self,task_id:str)->CrossNodeRecoveryBundle:
        with self.db.connect() as con: row=con.execute('SELECT * FROM fabric_checkpoints WHERE task_id=?',(task_id,)).fetchone()
        if not row: raise KeyError(task_id)
        raw=self.objects.get(row['object_hash'])
        return CrossNodeRecoveryBundle(_mission_from_dict(raw['mission']),DagEngine.from_snapshot(raw['dag']),RetryLedger.from_snapshot(raw['retry_ledger']),int(raw['generation']),raw['node_id'])
