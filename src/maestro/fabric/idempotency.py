from __future__ import annotations
import hashlib,json,time
from typing import Any
from .sqlite_backend import FabricDatabase

class IdempotencyConflict(RuntimeError): pass

class IdempotencyStore:
    def __init__(self,db:FabricDatabase): self.db=db
    @staticmethod
    def request_hash(payload:dict[str,Any])->str:
        raw=json.dumps(payload,sort_keys=True,separators=(',',':')).encode(); return hashlib.sha256(raw).hexdigest()
    def begin(self,key:str,payload:dict[str,Any])->bool:
        h=self.request_hash(payload); now=time.time()
        with self.db.immediate() as con:
            row=con.execute('SELECT request_hash FROM fabric_idempotency WHERE key=?',(key,)).fetchone()
            if row:
                if row['request_hash']!=h: raise IdempotencyConflict('Idempotency key reused with different request.')
                return False
            con.execute('INSERT INTO fabric_idempotency(key,request_hash,status,created_at,updated_at) VALUES(?,?,?,?,?)',(key,h,'IN_PROGRESS',now,now))
        return True
    def complete(self,key:str,result:dict[str,Any])->None:
        with self.db.immediate() as con:
            con.execute('UPDATE fabric_idempotency SET status=?,result_json=?,updated_at=? WHERE key=?',('DONE',json.dumps(result,sort_keys=True),time.time(),key))
    def result(self,key:str)->dict[str,Any]|None:
        with self.db.connect() as con: row=con.execute('SELECT status,result_json FROM fabric_idempotency WHERE key=?',(key,)).fetchone()
        if not row or row['status']!='DONE': return None
        return json.loads(row['result_json'])
