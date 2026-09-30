from __future__ import annotations
from dataclasses import dataclass
import json,time
from .backend import ClusterBackend

@dataclass(slots=True)
class NodeRecord:
    node_id:str; state:str='ONLINE'; metadata:dict|None=None; last_heartbeat:float=0.0

class NodeDirectory:
    def __init__(self,backend:ClusterBackend): self.backend=backend
    def advertise(self,node:NodeRecord)->None:
        now=time.time(); node.last_heartbeat=now
        with self.backend.immediate() as con:
            con.execute('INSERT OR REPLACE INTO cluster_nodes(node_id,state,last_heartbeat,metadata_json) VALUES(?,?,?,?)',(node.node_id,node.state,now,json.dumps(node.metadata or {},sort_keys=True)))
    def heartbeat(self,node_id:str)->None:
        with self.backend.immediate() as con:
            row=con.execute('SELECT node_id FROM cluster_nodes WHERE node_id=?',(node_id,)).fetchone()
            if not row: raise KeyError(node_id)
            con.execute('UPDATE cluster_nodes SET last_heartbeat=?,state=? WHERE node_id=?',(time.time(),'ONLINE',node_id))
    def mark(self,node_id:str,state:str)->None:
        with self.backend.immediate() as con:
            con.execute('UPDATE cluster_nodes SET state=?,last_heartbeat=? WHERE node_id=?',(state,time.time(),node_id))
    def live(self,max_age_seconds:int=60)->list[NodeRecord]:
        now=time.time()
        with self.backend.connect() as con: rows=con.execute('SELECT * FROM cluster_nodes WHERE state=? AND last_heartbeat>=?',('ONLINE',now-max_age_seconds)).fetchall()
        return [NodeRecord(r['node_id'],r['state'],json.loads(r['metadata_json']),r['last_heartbeat']) for r in rows]
