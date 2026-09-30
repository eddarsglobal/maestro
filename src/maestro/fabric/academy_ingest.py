from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4
import time
from maestro.storage.object_store import BinaryObjectStore
from .sqlite_backend import FabricDatabase

ACADEMY_BATCH_OBJECT_TYPE=0x63
@dataclass(frozen=True,slots=True)
class AcademyBatchRef:
    batch_id:str; object_hash:str; items:int

class AcademyBatchIngestor:
    def __init__(self,db:FabricDatabase,objects:BinaryObjectStore): self.db=db; self.objects=objects
    def ingest(self,scenario_results:list[dict],shadow_observations:list[dict])->AcademyBatchRef:
        batch_id=f'ABT-{uuid4().hex[:12].upper()}'; payload={'batch_id':batch_id,'scenario_results':scenario_results,'shadow_observations':shadow_observations}
        ref=self.objects.put(ACADEMY_BATCH_OBJECT_TYPE,payload)
        with self.db.immediate() as con: con.execute('INSERT INTO fabric_academy_batches(batch_id,object_hash,status,created_at) VALUES(?,?,?,?)',(batch_id,ref.sha256,'PENDING',time.time()))
        return AcademyBatchRef(batch_id,ref.sha256,len(scenario_results)+len(shadow_observations))
    def pending(self,limit:int=100)->list[AcademyBatchRef]:
        with self.db.connect() as con: rows=con.execute('SELECT * FROM fabric_academy_batches WHERE status=? ORDER BY created_at LIMIT ?',('PENDING',limit)).fetchall()
        out=[]
        for r in rows:
            raw=self.objects.get(r['object_hash']); out.append(AcademyBatchRef(r['batch_id'],r['object_hash'],len(raw['scenario_results'])+len(raw['shadow_observations'])))
        return out
    def consume(self,batch_id:str)->dict:
        with self.db.immediate() as con:
            row=con.execute('SELECT * FROM fabric_academy_batches WHERE batch_id=?',(batch_id,)).fetchone()
            if not row: raise KeyError(batch_id)
            con.execute('UPDATE fabric_academy_batches SET status=?,consumed_at=? WHERE batch_id=?',('CONSUMED',time.time(),batch_id))
        return self.objects.get(row['object_hash'])
