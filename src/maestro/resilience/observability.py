from __future__ import annotations
from dataclasses import dataclass,asdict
import time
from .backend import ClusterBackend

@dataclass(frozen=True,slots=True)
class ClusterSnapshot:
    queued:int; leased:int; done:int; failed:int
    online_workers:int; stale_workers:int; live_nodes:int
    active_fenced_locks:int; prepared_effects:int; committed_effects:int
    checkpoints:int; academy_pending:int
    def to_dict(self): return asdict(self)

class ClusterObservability:
    def __init__(self,backend:ClusterBackend): self.backend=backend
    def snapshot(self,worker_max_age_seconds:int=60)->ClusterSnapshot:
        now=time.time()
        with self.backend.connect() as con:
            counts={r['status']:r['n'] for r in con.execute('SELECT status,COUNT(*) n FROM fabric_work GROUP BY status').fetchall()}
            online=con.execute('SELECT COUNT(*) n FROM fabric_workers WHERE state=? AND last_heartbeat>=?',('ONLINE',now-worker_max_age_seconds)).fetchone()['n']
            stale=con.execute('SELECT COUNT(*) n FROM fabric_workers WHERE state=? AND last_heartbeat<?',('ONLINE',now-worker_max_age_seconds)).fetchone()['n']
            nodes=con.execute('SELECT COUNT(*) n FROM cluster_nodes WHERE state=?',('ONLINE',)).fetchone()['n']
            locks=con.execute('SELECT COUNT(*) n FROM cluster_fenced_locks WHERE expires_at>?',(now,)).fetchone()['n']
            effects={r['status']:r['n'] for r in con.execute('SELECT status,COUNT(*) n FROM cluster_effects GROUP BY status').fetchall()}
            cps=con.execute('SELECT COUNT(*) n FROM fabric_checkpoints').fetchone()['n']
            ap=con.execute('SELECT COUNT(*) n FROM fabric_academy_batches WHERE status=?',('PENDING',)).fetchone()['n']
        return ClusterSnapshot(counts.get('QUEUED',0),counts.get('LEASED',0),counts.get('DONE',0),counts.get('FAILED',0),online,stale,nodes,locks,effects.get('PREPARED',0),effects.get('COMMITTED',0),cps,ap)
