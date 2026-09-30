from __future__ import annotations
import sqlite3
from pathlib import Path
from contextlib import contextmanager

SCHEMA = r"""
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
CREATE TABLE IF NOT EXISTS fabric_work (
    work_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    council TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    priority INTEGER NOT NULL,
    status TEXT NOT NULL,
    idempotency_key TEXT UNIQUE,
    leased_by TEXT,
    lease_expires REAL,
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fabric_work_status_priority ON fabric_work(status, priority, created_at);
CREATE TABLE IF NOT EXISTS fabric_idempotency (
    key TEXT PRIMARY KEY,
    request_hash TEXT NOT NULL,
    status TEXT NOT NULL,
    result_json TEXT,
    created_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS fabric_locks (
    lock_name TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    token TEXT NOT NULL,
    expires_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS fabric_workers (
    worker_id TEXT PRIMARY KEY,
    councils_json TEXT NOT NULL,
    capabilities_json TEXT NOT NULL,
    node_id TEXT NOT NULL,
    load REAL NOT NULL,
    state TEXT NOT NULL,
    last_heartbeat REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS fabric_checkpoints (
    task_id TEXT PRIMARY KEY,
    object_hash TEXT NOT NULL,
    generation INTEGER NOT NULL,
    node_id TEXT NOT NULL,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS fabric_academy_batches (
    batch_id TEXT PRIMARY KEY,
    object_hash TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at REAL NOT NULL,
    consumed_at REAL
);

CREATE TABLE IF NOT EXISTS cluster_fence_counters (
    lock_name TEXT PRIMARY KEY,
    next_token INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS cluster_fenced_locks (
    lock_name TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    fencing_token INTEGER NOT NULL,
    lease_id TEXT NOT NULL,
    expires_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS cluster_effects (
    effect_key TEXT PRIMARY KEY,
    request_hash TEXT NOT NULL,
    status TEXT NOT NULL,
    fencing_token INTEGER,
    result_json TEXT,
    prepared_at REAL NOT NULL,
    updated_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS cluster_nodes (
    node_id TEXT PRIMARY KEY,
    state TEXT NOT NULL,
    last_heartbeat REAL NOT NULL,
    metadata_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cluster_worker_nonces (
    worker_id TEXT NOT NULL,
    nonce TEXT NOT NULL,
    expires_at REAL NOT NULL,
    consumed INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(worker_id, nonce)
);
CREATE TABLE IF NOT EXISTS cluster_placement_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    council TEXT NOT NULL,
    success INTEGER NOT NULL,
    latency_ms REAL NOT NULL,
    cost_units REAL NOT NULL,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS cluster_chaos_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    target TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at REAL NOT NULL
);
"""

class FabricDatabase:
    def __init__(self, path: str | Path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as con: con.executescript(SCHEMA)

    def connect(self):
        con=sqlite3.connect(self.path, timeout=30.0, isolation_level=None)
        con.row_factory=sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON')
        con.execute('PRAGMA busy_timeout=30000')
        return con

    @contextmanager
    def immediate(self):
        con=self.connect()
        try:
            con.execute('BEGIN IMMEDIATE')
            yield con
            con.execute('COMMIT')
        except Exception:
            con.execute('ROLLBACK'); raise
        finally: con.close()
