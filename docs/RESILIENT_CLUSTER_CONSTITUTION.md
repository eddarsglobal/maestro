# MAESTRO Resilient Cluster Constitution

## RC-01 — A lease is not enough for dangerous shared effects
Shared resources use monotonic fencing tokens so a stale worker cannot act after lease loss.

## RC-02 — Exactly-once is never claimed without target cooperation
MAESTRO provides idempotency keys, an effect journal and fencing. External systems must honor idempotency/fencing for non-duplicable effects.

## RC-03 — Worker identity is authenticated
The reference implementation uses HMAC challenge/response. Production deployments may replace it with mTLS or public-key identities without changing APTE.

## RC-04 — Capability filters are hard constraints
Placement learning may rank eligible workers only. It may not place a Council onto an unauthorized worker.

## RC-05 — Chaos is explicit
Failure injection is test/staging behavior and is never activated implicitly.

## RC-06 — Observability is read-only
Cluster metrics cannot mutate constitutional state.

## RC-07 — Backend is an adapter
SQLite/WAL is the lightweight reference backend. Redis/PostgreSQL/custom coordination services may replace it through the backend contract.

## RC-08 — Fencing tokens are monotonic per protected resource
A lower token is stale by definition.

## RC-09 — Node failure does not imply task failure
Expired leases are reclaimed; mission truth remains in durable state/checkpoints.

## RC-10 — Learning placement cannot erase safety
Historical success, cost and latency can improve placement ranking, never permissions.
