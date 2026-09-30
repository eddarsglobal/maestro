from __future__ import annotations
from dataclasses import dataclass
from .workers import WorkerDirectory, WorkerAdvertisement

@dataclass(frozen=True,slots=True)
class PlacementDecision:
    worker_id:str; node_id:str; score:float; reasons:tuple[str,...]

class CouncilPlacementStrategy:
    def __init__(self,directory:WorkerDirectory): self.directory=directory
    def place(self,council:str,required_capabilities:set[str]|None=None,preferred_node:str|None=None)->PlacementDecision|None:
        workers=self.directory.discover(council,required_capabilities or set())
        if not workers: return None
        ranked=[]
        for w in workers:
            score=max(0.0,1.0-min(1.0,w.load))
            reasons=[f'load={w.load:.3f}']
            if preferred_node and w.node_id==preferred_node: score+=0.20; reasons.append('node_locality')
            if required_capabilities: score+=min(0.10,0.01*len(required_capabilities)); reasons.append('capability_match')
            ranked.append((score,w,reasons))
        score,w,reasons=sorted(ranked,key=lambda x:(-x[0],x[1].worker_id))[0]
        return PlacementDecision(w.worker_id,w.node_id,score,tuple(reasons))
