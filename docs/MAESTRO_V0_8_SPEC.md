# MAESTRO v0.8 — DISTRIBUTED INTELLIGENCE FABRIC

## Objective
Make MAESTRO horizontally scalable without making the microkernel heavy.

## Fabric primitives
- persistent SQLite/WAL reference queue;
- lease heartbeat + expired-work reclaim;
- idempotency store;
- distributed lock reference implementation;
- worker capability directory;
- Council placement strategy;
- MBOS-backed context broker;
- cross-node checkpoint registry;
- Academy batch ingestion;
- safe Skill DAG transitive reduction.

## Important limitation
SQLite/WAL is the lightweight reference backend, appropriate for local/multi-process operation and some shared deployments. Production multi-host installations should plug in a transactional PostgreSQL/Redis-class backend. The Fabric API, not SQLite, is the architecture.

## Work lifecycle
`QUEUED -> LEASED -> DONE/FAILED`, with expired leases reclaimed to `QUEUED`.

## Placement
Placement considers Council allowlist, required capabilities, current worker load, and optional node locality.

## Contexts
Heavy Council context is stored once in MBOS and workers receive content hashes/references.

## Cross-node recovery
Latest task checkpoint is indexed transactionally and its payload is stored in the content-addressed object store.

## Skill optimization
v0.8 only performs semantics-preserving transitive reduction. It does not guess that two steps are independent.
