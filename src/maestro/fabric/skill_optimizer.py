from __future__ import annotations
from dataclasses import dataclass
from maestro.orchestration.dag import DagEngine,DagNode

@dataclass(slots=True)
class SkillOptimizationReport:
    removed_edges:list[tuple[str,str]]
    original_edges:int
    optimized_edges:int
    max_parallel_ready:int

class SkillGraphOptimizer:
    """Safe transitive reduction: removes only dependency edges already implied by another path."""
    @staticmethod
    def _reachable(dag:DagEngine,start:str,target:str,skip_edge:tuple[str,str]|None=None)->bool:
        # graph stored child -> dependencies; traverse dependency direction
        stack=[start]; seen=set()
        while stack:
            cur=stack.pop()
            if cur==target: return True
            if cur in seen: continue
            seen.add(cur)
            for dep in dag.nodes[cur].depends_on:
                if skip_edge==(cur,dep): continue
                stack.append(dep)
        return False
    def optimize(self,dag:DagEngine)->tuple[DagEngine,SkillOptimizationReport]:
        out=DagEngine.from_snapshot(dag.snapshot()); removed=[]
        original=sum(len(n.depends_on) for n in out.nodes.values())
        for node_id in list(out.nodes):
            for dep in list(out.nodes[node_id].depends_on):
                if self._reachable(out,node_id,dep,skip_edge=(node_id,dep)):
                    out.nodes[node_id].depends_on.remove(dep); removed.append((node_id,dep))
        out.validate_acyclic()
        optimized=sum(len(n.depends_on) for n in out.nodes.values())
        # structural parallelism estimate by Kahn layers without mutating node state
        deps={nid:set(n.depends_on) for nid,n in out.nodes.items()}; done=set(); max_ready=0
        while len(done)<len(deps):
            ready=[nid for nid,d in deps.items() if nid not in done and d.issubset(done)]
            if not ready: break
            max_ready=max(max_ready,len(ready)); done.update(ready)
        return out,SkillOptimizationReport(removed,original,optimized,max_ready)
