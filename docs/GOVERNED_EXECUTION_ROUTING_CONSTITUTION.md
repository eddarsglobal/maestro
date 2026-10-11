# MAESTRO Governed Execution Routing Constitution

## Scope

GER0.1 governs:

- BM2-016 Execution Routing
- BM2-017 Parallelism
- BM2-018 Distributed Runtime

It bridges an execution-eligible governed mission plan to existing
Council execution, async and distributed Fabric mechanisms.

GER0.1 itself performs no execution.

## GER-01 — Execution routing requires validated plan lineage

Routing SHALL bind:

- governed mission plan
- governed plan validation
- explicit downstream authorization evidence

Cross-lineage evidence SHALL fail closed.

PLAN ELIGIBLE != ROUTE AUTHORIZED.

## GER-02 — EX remains the execution authority

Execution routing SHALL require explicit PASS evidence for EX
authorization.

Workers, adapters, models, providers and runtimes SHALL NOT gain
EX authority.

ROUTED BY EX != AUTHORITY TRANSFERRED.

WORKER EXECUTES != WORKER AUTHORIZES.

## GER-03 — Effect authorization remains distinct

Effect authorization evidence SHALL be explicit and PASS before an
execution route may be emitted.

EX AUTHORIZED != EFFECT AUTHORIZED.

EFFECT AUTHORIZED != EFFECT EXECUTED.

## GER-04 — Every plan node routes exactly once

Each mission-plan node SHALL produce one deterministic execution route
binding:

- node
- capability
- owning Council
- selected resource
- idempotency key

ROUTE CREATED != NODE EXECUTED.

## GER-05 — Independent nodes may run concurrently

Nodes whose dependencies are already satisfied MAY appear in the
same execution wave.

Parallelism SHALL never violate DAG dependencies.

PARALLEL ELIGIBLE != PARALLEL EXECUTED.

CONCURRENT != UNORDERED.

## GER-06 — Parallelism is bounded

Execution waves SHALL obey an explicit maximum parallelism bound.

Excess independent work SHALL be partitioned deterministically.

AVAILABLE PARALLELISM != UNBOUNDED EXECUTION.

## GER-07 — Worker placement is capability-aware

A worker SHALL be placement-eligible only when it explicitly supports:

- owning Council
- required capability
- active capacity

WORKER AVAILABLE != WORKER ELIGIBLE.

## GER-08 — Distributed execution requires lease and duplicate protection

Distributed or local worker placement SHALL require explicit PASS
evidence for:

- online state
- lease validity
- exact plan/node lease binding
- duplicate-execution protection
- recovery readiness

LEASED != AUTHORIZED.

LEASE VALID != MISSION AUTHORITY.

DUPLICATE GUARD != EXECUTION AUTHORITY.

## GER-09 — Worker placement is deterministic and authority-neutral

Equivalent eligible worker evidence SHALL produce deterministic placement.

Worker load and stable identity may influence placement.

No worker, node, adapter, provider, model or runtime gains mission authority.

PLACEMENT != AUTHORITY.

RESOURCE EXECUTION != MISSION AUTHORITY.

## GER-10 — Existing execution engines remain downstream

GER0.1 SHALL NOT replace:

- CouncilExecutor
- AsyncCouncilRunner
- DagEngine
- Fabric queue
- worker directory
- Fabric leases
- idempotency ledger
- cross-node recovery

Those components remain downstream operational mechanisms.

GER0.1 creates routing evidence and execution waves only.

ROUTING PLAN != EXECUTION.

## Canonical boundary

EXECUTION-ELIGIBLE PLAN
        |
        +
EX AUTHORIZATION EVIDENCE
        |
        +
EFFECT AUTHORIZATION EVIDENCE
        |
        v
DETERMINISTIC EXECUTION ROUTES
        |
        v
DEPENDENCY-SAFE WAVES
        |
        +---- BOUNDED PARALLELISM
        |
        v
WORKER EVIDENCE
        |
        +---- COUNCIL MATCH
        +---- CAPABILITY MATCH
        +---- ONLINE
        +---- LEASE VALID
        +---- PLAN/NODE BINDING
        +---- DUPLICATE GUARD
        +---- RECOVERY READY
        +---- CAPACITY
        |
        v
DETERMINISTIC WORKER PLACEMENT
        |
        v
BOUNDARY STOPS
        |
        v
EXISTING EXECUTION / ASYNC / FABRIC RUNTIMES

## Constitutional separations

PLAN ELIGIBLE != ROUTE AUTHORIZED

ROUTED BY EX != AUTHORITY TRANSFERRED

WORKER EXECUTES != WORKER AUTHORIZES

EX AUTHORIZED != EFFECT AUTHORIZED

EFFECT AUTHORIZED != EFFECT EXECUTED

ROUTE CREATED != NODE EXECUTED

PARALLEL ELIGIBLE != PARALLEL EXECUTED

AVAILABLE PARALLELISM != UNBOUNDED EXECUTION

WORKER AVAILABLE != WORKER ELIGIBLE

LEASED != AUTHORIZED

LEASE VALID != MISSION AUTHORITY

DUPLICATE GUARD != EXECUTION AUTHORITY

PLACEMENT != AUTHORITY

RESOURCE EXECUTION != MISSION AUTHORITY

ROUTING PLAN != EXECUTION

## Final invariant

MAESTRO MAY ROUTE AN EXPLICITLY EX-AUTHORIZED AND EFFECT-AUTHORIZED
MISSION PLAN INTO DETERMINISTIC COUNCIL-BOUND EXECUTION ROUTES,
BOUNDED DEPENDENCY-SAFE PARALLEL WAVES AND LEASE-VALID DISTRIBUTED
WORKER PLACEMENTS WITHOUT TRANSFERRING MISSION OR EXECUTION AUTHORITY
TO WORKERS, MODELS, PROVIDERS, ADAPTERS OR RUNTIMES.
