from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4
import time
from .sqlite_backend import FabricDatabase

@dataclass(frozen=True,slots=True)
class LockRecord:
    lock_name:str; owner_id:str; token:str; expires_at:float

class DistributedLockManager:
    def __init__(self,db:FabricDatabase): self.db=db
    def acquire(self,lock_name:str,owner_id:str,ttl_seconds:int=30)->LockRecord|None:
        now=time.time(); token=f'LCK-{uuid4().hex[:16].upper()}'
        with self.db.immediate() as con:
            row=con.execute('SELECT * FROM fabric_locks WHERE lock_name=?',(lock_name,)).fetchone()
            if row and row['expires_at']>now: return None
            con.execute('INSERT OR REPLACE INTO fabric_locks(lock_name,owner_id,token,expires_at,updated_at) VALUES(?,?,?,?,?)',(lock_name,owner_id,token,now+ttl_seconds,now))
        return LockRecord(lock_name,owner_id,token,now+ttl_seconds)
    def heartbeat(self,lock_name:str,owner_id:str,token:str,ttl_seconds:int=30)->LockRecord:
        now=time.time()
        with self.db.immediate() as con:
            row=con.execute('SELECT * FROM fabric_locks WHERE lock_name=?',(lock_name,)).fetchone()
            if not row or row['owner_id']!=owner_id or row['token']!=token or row['expires_at']<=now: raise PermissionError('Lock not owned or expired.')
            exp=now+ttl_seconds; con.execute('UPDATE fabric_locks SET expires_at=?,updated_at=? WHERE lock_name=?',(exp,now,lock_name))
        return LockRecord(lock_name,owner_id,token,exp)
    def release(self,lock_name:str,owner_id:str,token:str)->None:
        with self.db.immediate() as con:
            row=con.execute('SELECT owner_id,token FROM fabric_locks WHERE lock_name=?',(lock_name,)).fetchone()
            if not row or row['owner_id']!=owner_id or row['token']!=token: raise PermissionError('Lock not owned.')
            con.execute('DELETE FROM fabric_locks WHERE lock_name=?',(lock_name,))
    def reap_expired(self)->int:
        with self.db.immediate() as con:
            cur=con.execute('DELETE FROM fabric_locks WHERE expires_at<=?',(time.time(),)); return cur.rowcount
