from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
import hashlib,json,time
from .backend import ClusterBackend

class EffectConflict(RuntimeError): pass
class StaleEffectFence(PermissionError): pass
class EffectState(StrEnum): PREPARED='PREPARED'; COMMITTED='COMMITTED'; ABORTED='ABORTED'

@dataclass(frozen=True,slots=True)
class EffectRecord:
    effect_key:str; request_hash:str; state:EffectState; fencing_token:int|None; result:dict[str,Any]|None

class EffectJournal:
    """Idempotent effect protocol. External target should honor the same key/fence when possible."""
    def __init__(self,backend:ClusterBackend): self.backend=backend
    @staticmethod
    def _hash(payload:dict[str,Any])->str:
        return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

    def prepare(self,effect_key:str,payload:dict[str,Any],fencing_token:int|None=None)->tuple[EffectRecord,bool]:
        h=self._hash(payload); now=time.time()
        with self.backend.immediate() as con:
            row=con.execute('SELECT * FROM cluster_effects WHERE effect_key=?',(effect_key,)).fetchone()
            if row:
                if row['request_hash']!=h: raise EffectConflict('Effect key reused with a different payload.')
                rec=self._row(row); return rec,False
            con.execute('INSERT INTO cluster_effects(effect_key,request_hash,status,fencing_token,prepared_at,updated_at) VALUES(?,?,?,?,?,?)',(effect_key,h,EffectState.PREPARED.value,fencing_token,now,now))
        return EffectRecord(effect_key,h,EffectState.PREPARED,fencing_token,None),True

    def commit(self,effect_key:str,result:dict[str,Any],fencing_token:int|None=None)->EffectRecord:
        now=time.time()
        with self.backend.immediate() as con:
            row=con.execute('SELECT * FROM cluster_effects WHERE effect_key=?',(effect_key,)).fetchone()
            if not row: raise KeyError(effect_key)
            existing=row['fencing_token']
            if existing is not None and fencing_token is not None and int(fencing_token)<int(existing): raise StaleEffectFence('Stale fencing token.')
            if row['status']==EffectState.COMMITTED.value: return self._row(row)
            if row['status']==EffectState.ABORTED.value: raise EffectConflict('Cannot commit aborted effect.')
            con.execute('UPDATE cluster_effects SET status=?,fencing_token=?,result_json=?,updated_at=? WHERE effect_key=?',(EffectState.COMMITTED.value,fencing_token if fencing_token is not None else existing,json.dumps(result,sort_keys=True),now,effect_key))
            row=con.execute('SELECT * FROM cluster_effects WHERE effect_key=?',(effect_key,)).fetchone()
        return self._row(row)

    def abort(self,effect_key:str)->None:
        with self.backend.immediate() as con:
            row=con.execute('SELECT status FROM cluster_effects WHERE effect_key=?',(effect_key,)).fetchone()
            if not row: raise KeyError(effect_key)
            if row['status']==EffectState.COMMITTED.value: raise EffectConflict('Committed effect cannot be aborted.')
            con.execute('UPDATE cluster_effects SET status=?,updated_at=? WHERE effect_key=?',(EffectState.ABORTED.value,time.time(),effect_key))

    def get(self,effect_key:str)->EffectRecord:
        with self.backend.connect() as con: row=con.execute('SELECT * FROM cluster_effects WHERE effect_key=?',(effect_key,)).fetchone()
        if not row: raise KeyError(effect_key)
        return self._row(row)

    @staticmethod
    def _row(row)->EffectRecord:
        return EffectRecord(row['effect_key'],row['request_hash'],EffectState(row['status']),row['fencing_token'],json.loads(row['result_json']) if row['result_json'] else None)
