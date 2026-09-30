from __future__ import annotations
from pathlib import Path
from maestro.fabric import DistributedIntelligenceFabric
from .backend import SQLiteClusterBackend
from .fencing import FencedLockManager
from .identity import WorkerIdentityAuthority
from .effects import EffectJournal
from .nodes import NodeDirectory
from .chaos import ChaosHarness
from .observability import ClusterObservability
from .placement_learning import AdaptiveClusterPlacement

class ResilientCluster:
    """v0.9 composition root. Keeps v0.8 fabric intact and layers resilience above it."""
    def __init__(self,root:str|Path):
        self.fabric=DistributedIntelligenceFabric(root)
        self.backend=SQLiteClusterBackend(self.fabric.db)
        self.fencing=FencedLockManager(self.backend)
        self.identity=WorkerIdentityAuthority(self.backend)
        self.effects=EffectJournal(self.backend)
        self.nodes=NodeDirectory(self.backend)
        self.chaos=ChaosHarness(self.backend)
        self.observability=ClusterObservability(self.backend)
        self.placement=AdaptiveClusterPlacement(self.backend,self.fabric.workers)
