from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4
import time
from maestro.fabric.workers import WorkerDirectory
from maestro.fabric.placement import PlacementDecision
from .backend import ClusterBackend

@dataclass(frozen=True,slots=True)
class PlacementObservation:
    worker_id:str; node_id:str; council:str; success:bool; latency_ms:float; cost_units:float

class AdaptiveClusterPlacement:
    """Hard capability filtering first, learned performance preference second."""
    def __init__(self,backend:ClusterBackend,directory:WorkerDirectory): self.backend=backend; self.directory=directory
    def observe(self,o:PlacementObservation)->None:
        with self.backend.immediate() as con:
            con.execute('INSERT INTO cluster_placement_observations(worker_id,node_id,council,success,latency_ms,cost_units,created_at) VALUES(?,?,?,?,?,?,?)',(o.worker_id,o.node_id,o.council,int(o.success),float(o.latency_ms),float(o.cost_units),time.time()))
    def place(self,council:str,required_capabilities:set[str]|None=None,preferred_node:str|None=None)->PlacementDecision|None:
        workers=self.directory.discover(council,required_capabilities or set())
        if not workers: return None
        ranked=[]
        with self.backend.connect() as con:
            for w in workers:
                rows=con.execute('SELECT success,latency_ms,cost_units FROM cluster_placement_observations WHERE worker_id=? AND council=? ORDER BY observation_id DESC LIMIT 100',(w.worker_id,council)).fetchall()
                if rows:
                    success=sum(r['success'] for r in rows)/len(rows); latency=sum(r['latency_ms'] for r in rows)/len(rows); cost=sum(r['cost_units'] for r in rows)/len(rows)
                    learned=0.55*success + 0.25*max(0,1-min(1,latency/100000.0)) + 0.20*max(0,1-min(1,cost/100.0))
                    reasons=[f'history={len(rows)}',f'success={success:.3f}']
                else:
                    learned=0.50; reasons=['history=0']
                load_component=max(0.0,1.0-min(1.0,w.load))
                score=0.65*learned+0.35*load_component
                if preferred_node and w.node_id==preferred_node: score+=0.10; reasons.append('node_locality')
                ranked.append((score,w,reasons))
        score,w,reasons=sorted(ranked,key=lambda x:(-x[0],x[1].worker_id))[0]
        return PlacementDecision(w.worker_id,w.node_id,score,tuple(reasons))
