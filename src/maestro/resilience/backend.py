from __future__ import annotations
from typing import Protocol, ContextManager, Any
from maestro.fabric.sqlite_backend import FabricDatabase

class ClusterBackend(Protocol):
    """Minimal coordination backend contract used by resilient cluster services."""
    def connect(self): ...
    def immediate(self) -> ContextManager[Any]: ...

class SQLiteClusterBackend:
    """Reference zero-dependency backend. Replaceable by future adapters."""
    def __init__(self, database: FabricDatabase): self.database=database
    @property
    def path(self): return self.database.path
    def connect(self): return self.database.connect()
    def immediate(self): return self.database.immediate()
