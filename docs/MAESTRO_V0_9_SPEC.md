# MAESTRO v0.9 — RESILIENT CLUSTER

## Objective
Make the distributed intelligence fabric resilient to stale workers, duplicated delivery, node loss and learned placement errors while preserving a tiny provider-independent core.

## New layers

### Backend abstraction
Cluster coordination code targets a minimal backend contract. SQLite/WAL remains the zero-dependency reference implementation.

### Fencing
Every protected shared-resource lease receives a monotonically increasing fencing token.
Old workers may still be alive, but their old token is rejected.

### Cryptographic worker identity
Reference HMAC challenge/response prevents a worker from joining merely by knowing an ID. The protocol is replaceable by mTLS/Ed25519 adapters.

### Effect journal
External side effects follow:
`PREPARE -> EXECUTE WITH IDEMPOTENCY KEY/FENCE -> COMMIT`
A duplicate request with the same key/payload can reuse state; a conflicting payload is rejected.

### Chaos harness
Controlled failure injection can expire workers/work leases or fail a node to exercise recovery.

### Cluster observability
Compact snapshots expose work state, worker health, nodes, locks, effects, checkpoints and Academy backlog.

### Adaptive placement
Hard Council/capability authorization filters are applied first. Historical success, latency, cost, load and locality rank only the eligible workers.
