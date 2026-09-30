from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import uuid4
import json, time
from .sqlite_backend import FabricDatabase

class FabricWorkStatus(StrEnum):
    QUEUED='QUEUED'; LEASED='LEASED'; DONE='DONE'; FAILED='FAILED'

@dataclass(slots=True)
class FabricWorkItem:
    task_id: str
    council: str
    action: str
    payload: dict[str,Any]=field(default_factory=dict)
    priority: int=100
    idempotency_key: str|None=None
    work_id: str=field(default_factory=lambda:f'FWRK-{uuid4().hex[:12].upper()}')
    status: FabricWorkStatus=FabricWorkStatus.QUEUED
    leased_by: str|None=None
    attempts: int=0

class PersistentWorkQueue:
    def __init__(self, db: FabricDatabase): self.db=db

    def enqueue(self,item:FabricWorkItem)->str:
        now=time.time()
        with self.db.immediate() as con:
            if item.idempotency_key:
                row=con.execute('SELECT work_id FROM fabric_work WHERE idempotency_key=?',(item.idempotency_key,)).fetchone()
                if row: return row['work_id']
            con.execute('INSERT INTO fabric_work(work_id,task_id,council,action,payload_json,priority,status,idempotency_key,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)',
                (item.work_id,item.task_id,item.council,item.action,json.dumps(item.payload,sort_keys=True),item.priority,item.status.value,item.idempotency_key,now,now))
        return item.work_id

    def lease_next(self,worker_id:str,allowed_councils:set[str],lease_seconds:int=30)->FabricWorkItem|None:
        if not allowed_councils: return None
        now=time.time(); placeholders=','.join('?' for _ in allowed_councils)
        params=[FabricWorkStatus.QUEUED.value,*sorted(allowed_councils)]
        with self.db.immediate() as con:
            row=con.execute(f'SELECT * FROM fabric_work WHERE status=? AND council IN ({placeholders}) ORDER BY priority ASC, created_at ASC LIMIT 1',params).fetchone()
            if not row: return None
            con.execute('UPDATE fabric_work SET status=?,leased_by=?,lease_expires=?,attempts=attempts+1,updated_at=? WHERE work_id=? AND status=?',
                (FabricWorkStatus.LEASED.value,worker_id,now+lease_seconds,now,row['work_id'],FabricWorkStatus.QUEUED.value))
            fresh=con.execute('SELECT * FROM fabric_work WHERE work_id=?',(row['work_id'],)).fetchone()
        return self._from_row(fresh)

    def heartbeat(self,work_id:str,worker_id:str,lease_seconds:int=30)->None:
        now=time.time()
        with self.db.immediate() as con:
            row=con.execute('SELECT status,leased_by FROM fabric_work WHERE work_id=?',(work_id,)).fetchone()
            if not row or row['status']!=FabricWorkStatus.LEASED.value or row['leased_by']!=worker_id: raise PermissionError('Worker does not own active lease.')
            con.execute('UPDATE fabric_work SET lease_expires=?,updated_at=? WHERE work_id=?',(now+lease_seconds,now,work_id))

    def complete(self,work_id:str,worker_id:str)->None: self._finish(work_id,worker_id,FabricWorkStatus.DONE)
    def fail(self,work_id:str,worker_id:str)->None: self._finish(work_id,worker_id,FabricWorkStatus.FAILED)

    def _finish(self,work_id,worker_id,status):
        now=time.time()
        with self.db.immediate() as con:
            row=con.execute('SELECT status,leased_by FROM fabric_work WHERE work_id=?',(work_id,)).fetchone()
            if not row or row['status']!=FabricWorkStatus.LEASED.value or row['leased_by']!=worker_id: raise PermissionError('Worker does not own active lease.')
            con.execute('UPDATE fabric_work SET status=?,leased_by=NULL,lease_expires=NULL,updated_at=? WHERE work_id=?',(status.value,now,work_id))

    def reclaim_expired(self)->list[str]:
        now=time.time()
        with self.db.immediate() as con:
            rows=con.execute('SELECT work_id FROM fabric_work WHERE status=? AND lease_expires IS NOT NULL AND lease_expires<=?',(FabricWorkStatus.LEASED.value,now)).fetchall()
            ids=[r['work_id'] for r in rows]
            if ids:
                con.executemany('UPDATE fabric_work SET status=?,leased_by=NULL,lease_expires=NULL,updated_at=? WHERE work_id=?',[(FabricWorkStatus.QUEUED.value,now,w) for w in ids])
        return ids

    def get(self,work_id:str)->FabricWorkItem:
        with self.db.connect() as con:
            row=con.execute('SELECT * FROM fabric_work WHERE work_id=?',(work_id,)).fetchone()
        if not row: raise KeyError(work_id)
        return self._from_row(row)

    @staticmethod
    def _from_row(row):
        return FabricWorkItem(task_id=row['task_id'],council=row['council'],action=row['action'],payload=json.loads(row['payload_json']),priority=row['priority'],idempotency_key=row['idempotency_key'],work_id=row['work_id'],status=FabricWorkStatus(row['status']),leased_by=row['leased_by'],attempts=row['attempts'])
