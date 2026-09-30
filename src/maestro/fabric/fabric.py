from __future__ import annotations
from pathlib import Path
from maestro.storage.object_store import BinaryObjectStore
from .sqlite_backend import FabricDatabase
from .queue import PersistentWorkQueue
from .idempotency import IdempotencyStore
from .locks import DistributedLockManager
from .workers import WorkerDirectory
from .placement import CouncilPlacementStrategy
from .context_broker import ContextBroker
from .recovery import CrossNodeCheckpointStore
from .academy_ingest import AcademyBatchIngestor
from .skill_optimizer import SkillGraphOptimizer

class DistributedIntelligenceFabric:
    """Composition root for v0.8 distributed-ready primitives."""
    def __init__(self,root:str|Path):
        root=Path(root); root.mkdir(parents=True,exist_ok=True)
        self.db=FabricDatabase(root/'fabric.sqlite3')
        self.objects=BinaryObjectStore(root/'objects')
        self.queue=PersistentWorkQueue(self.db)
        self.idempotency=IdempotencyStore(self.db)
        self.locks=DistributedLockManager(self.db)
        self.workers=WorkerDirectory(self.db)
        self.placement=CouncilPlacementStrategy(self.workers)
        self.contexts=ContextBroker(self.objects)
        self.checkpoints=CrossNodeCheckpointStore(self.db,self.objects)
        self.academy=AcademyBatchIngestor(self.db,self.objects)
        self.skill_optimizer=SkillGraphOptimizer()
