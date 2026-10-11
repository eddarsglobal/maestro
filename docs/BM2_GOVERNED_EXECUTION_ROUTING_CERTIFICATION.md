# BM2 Governed Execution Routing Certification

Checkpoint: GER0.1

## BM2-016 — Execution Routing — PASS

Certified properties:

- routing requires execution-eligible mission plan
- routing requires exact plan-validation lineage
- explicit EX authorization evidence is mandatory
- explicit effect authorization evidence is mandatory
- failed authorization rejects routing
- unknown authorization fails closed
- every mission-plan node routes exactly once
- route binds capability
- route binds owning Council
- route binds selected resource
- deterministic idempotency key
- adapters receive no mission authority
- resources receive no mission authority
- providers receive no mission authority
- models receive no mission authority
- workers receive no mission authority
- GER performs no execution

## BM2-017 — Parallelism — PASS

Certified properties:

- dependencies are preserved
- independent nodes may share an execution wave
- dependent nodes wait for prerequisite wave completion
- maximum parallelism is explicit
- excess ready work is partitioned deterministically
- wave ordering is deterministic
- every routed node appears in exactly one execution wave
- parallel eligibility does not execute work

## BM2-018 — Distributed Runtime — PASS

Certified properties:

- worker Council coverage is explicit
- worker capability coverage is explicit
- worker online evidence is explicit
- worker lease evidence is explicit
- lease binds exact plan
- lease binds exact plan node
- duplicate-execution guard evidence is explicit
- recovery readiness evidence is explicit
- worker capacity is explicit
- exhausted worker capacity fails closed
- failed lease fails closed
- unknown duplicate protection fails closed
- deterministic worker placement
- local and distributed workers are supported
- existing Fabric lease/idempotency/recovery primitives remain downstream
- worker placement grants no authority

## BordingMap 2.0 state

TOTAL: 32

PASS: 18

DEFERRED: 14

BLOCKED: 0

MISSING: 0

NEXT: BM2-019

PROJECT_COMPLETE: FALSE

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
