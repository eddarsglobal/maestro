from __future__ import annotations
from dataclasses import dataclass
import json,time
from .sqlite_backend import FabricDatabase

@dataclass(slots=True)
class WorkerAdvertisement:
    worker_id:str; node_id:str; councils:set[str]; capabilities:set[str]; load:float=0.0; state:str='ONLINE'; last_heartbeat:float=0.0

class WorkerDirectory:
    def __init__(self,db:FabricDatabase): self.db=db
    def advertise(self,w:WorkerAdvertisement)->None:
        now=time.time(); w.last_heartbeat=now
        with self.db.immediate() as con:
            con.execute('INSERT OR REPLACE INTO fabric_workers(worker_id,councils_json,capabilities_json,node_id,load,state,last_heartbeat) VALUES(?,?,?,?,?,?,?)',(w.worker_id,json.dumps(sorted(w.councils)),json.dumps(sorted(w.capabilities)),w.node_id,float(w.load),w.state,now))
    def heartbeat(self,worker_id:str,load:float|None=None)->None:
        with self.db.immediate() as con:
            row=con.execute('SELECT worker_id FROM fabric_workers WHERE worker_id=?',(worker_id,)).fetchone()
            if not row: raise KeyError(worker_id)
            if load is None: con.execute('UPDATE fabric_workers SET last_heartbeat=? WHERE worker_id=?',(time.time(),worker_id))
            else: con.execute('UPDATE fabric_workers SET last_heartbeat=?,load=? WHERE worker_id=?',(time.time(),float(load),worker_id))
    def discover(self,council:str,required_capabilities:set[str]|None=None,max_age_seconds:int=60)->list[WorkerAdvertisement]:
        now=time.time(); required_capabilities=required_capabilities or set(); out=[]
        with self.db.connect() as con: rows=con.execute('SELECT * FROM fabric_workers WHERE state=? AND last_heartbeat>=?',('ONLINE',now-max_age_seconds)).fetchall()
        for r in rows:
            councils=set(json.loads(r['councils_json'])); caps=set(json.loads(r['capabilities_json']))
            if council not in councils or not required_capabilities.issubset(caps): continue
            out.append(WorkerAdvertisement(r['worker_id'],r['node_id'],councils,caps,r['load'],r['state'],r['last_heartbeat']))
        return sorted(out,key=lambda w:(w.load,w.node_id,w.worker_id))
