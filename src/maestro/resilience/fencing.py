from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4
import time
from .backend import ClusterBackend

class StaleFencingToken(PermissionError): pass

@dataclass(frozen=True,slots=True)
class FencedLease:
    lock_name:str
    owner_id:str
    fencing_token:int
    lease_id:str
    expires_at:float

class FencedLockManager:
    """Monotonic fencing tokens prevent an old owner from acting after lease loss."""
    def __init__(self, backend: ClusterBackend): self.backend=backend

    def acquire(self, lock_name:str, owner_id:str, ttl_seconds:int=30)->FencedLease|None:
        now=time.time(); lease_id=f'FLS-{uuid4().hex[:16].upper()}'
        with self.backend.immediate() as con:
            active=con.execute('SELECT * FROM cluster_fenced_locks WHERE lock_name=?',(lock_name,)).fetchone()
            if active and active['expires_at']>now: return None
            row=con.execute('SELECT next_token FROM cluster_fence_counters WHERE lock_name=?',(lock_name,)).fetchone()
            token=int(row['next_token']) if row else 1
            con.execute('INSERT OR REPLACE INTO cluster_fence_counters(lock_name,next_token) VALUES(?,?)',(lock_name,token+1))
            exp=now+ttl_seconds
            con.execute('INSERT OR REPLACE INTO cluster_fenced_locks(lock_name,owner_id,fencing_token,lease_id,expires_at,updated_at) VALUES(?,?,?,?,?,?)',(lock_name,owner_id,token,lease_id,exp,now))
        return FencedLease(lock_name,owner_id,token,lease_id,exp)

    def heartbeat(self, lease:FencedLease, ttl_seconds:int=30)->FencedLease:
        now=time.time()
        with self.backend.immediate() as con:
            row=con.execute('SELECT * FROM cluster_fenced_locks WHERE lock_name=?',(lease.lock_name,)).fetchone()
            if not row or row['owner_id']!=lease.owner_id or row['lease_id']!=lease.lease_id or int(row['fencing_token'])!=lease.fencing_token or row['expires_at']<=now:
                raise StaleFencingToken('Lease is stale, replaced, or expired.')
            exp=now+ttl_seconds
            con.execute('UPDATE cluster_fenced_locks SET expires_at=?,updated_at=? WHERE lock_name=?',(exp,now,lease.lock_name))
        return FencedLease(lease.lock_name,lease.owner_id,lease.fencing_token,lease.lease_id,exp)

    def release(self, lease:FencedLease)->None:
        with self.backend.immediate() as con:
            row=con.execute('SELECT * FROM cluster_fenced_locks WHERE lock_name=?',(lease.lock_name,)).fetchone()
            if not row or row['owner_id']!=lease.owner_id or row['lease_id']!=lease.lease_id or int(row['fencing_token'])!=lease.fencing_token:
                raise StaleFencingToken('Cannot release stale fencing lease.')
            con.execute('DELETE FROM cluster_fenced_locks WHERE lock_name=?',(lease.lock_name,))

    def validate_token(self, lock_name:str, fencing_token:int)->bool:
        with self.backend.connect() as con:
            row=con.execute('SELECT fencing_token,expires_at FROM cluster_fenced_locks WHERE lock_name=?',(lock_name,)).fetchone()
        return bool(row and int(row['fencing_token'])==int(fencing_token) and row['expires_at']>time.time())
