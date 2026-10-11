# BM2 Durable Mission Recovery Certification

Checkpoint: DMR0.1

## BM2-022 — Durable Mission — PASS

Certified properties:

- exact legacy runtime checkpoint binding
- runtime checkpoint schema binding
- runtime checkpoint SHA-256 binding
- canonical mission snapshot durability
- mission contract durability
- objective fingerprint durability
- governed mission plan durability
- DAG dependency durability
- routing-plan durability
- resource-binding durability
- execution-wave durability
- worker-placement durability
- idempotency-key durability
- node execution-evidence durability
- output-reference durability
- provenance-reference durability
- Council-verdict evidence durability
- node-acceptance evidence durability
- node-closure durability
- mission-verdict evidence durability
- mission-verdict artifact durability
- retry-state durability
- Council runtime-state durability
- recovery-information durability
- generation durability
- canonical serialization
- payload SHA-256
- envelope SHA-256
- atomic durable save
- governed load/resume
- exact checkpoint roundtrip
- semantic fingerprint preservation
- tamper detection
- unsupported schema fails closed
- lineage drift fails closed
- no execution authority from checkpoint
- no durable-commit authority from checkpoint
- no learning authority from checkpoint

## BM2-023 — Autonomous Recovery — PASS

Certified properties:

- recovery binds exact durable checkpoint
- recovery binds exact payload SHA-256
- recovery preserves objective fingerprint
- recovery cannot target future generation
- checkpoint integrity evidence is explicit
- failure evidence is explicit
- UNKNOWN recovery evidence fails closed
- failed checkpoint integrity is UNRECOVERABLE
- no failure composes HEALTHY state
- existing FCR containment composes CONTAINMENT_PROPOSED
- existing FCR rollback composes ROLLBACK_PROPOSED
- existing FCR recovery composes RESUME_PROPOSED
- existing FCR UNRECOVERABLE remains UNRECOVERABLE
- adaptive REPLAN_REQUIRED composes REPLAN_PROPOSED
- FCR action/state mismatch fails closed
- recovery decisions are deterministic
- recovery requires AY revalidation
- recovery requires EX reauthorization
- recovery layer executes no rollback
- recovery layer executes no recovery
- recovery layer executes no replanning
- recovery layer performs no canonical mission-state transition
- recovery layer grants no effect authority
- recovery layer grants no TX durable-commit authority
- recovery layer grants no learning authority
- recovery layer asserts no system truth

## BordingMap 2.0 state

TOTAL: 32

PASS: 23

DEFERRED: 9

BLOCKED: 0

MISSING: 0

NEXT: BM2-024

PROJECT_COMPLETE: FALSE

## Constitutional separations

MISSION SNAPSHOT != COMPLETE DURABLE MISSION

PHASE2 CHECKPOINT != LEGACY CHECKPOINT REPLACEMENT

CHECKPOINT PRESENT != CHECKPOINT INTACT

HASH MISMATCH != RECOVERABLE STATE

RESUME != REPLAN

RESUME != OBJECTIVE CHANGE

CHECKPOINTED != AUTHORIZED

RESTORED != EXECUTION AUTHORIZED

FCR PLAN != RECOVERY EXECUTION

RECOVERY PROPOSAL != RECOVERY EXECUTION

AUTONOMOUS DECISION != AUTONOMOUS EXECUTION

REPLAN PROPOSED != REPLAN EXECUTED

REPLAN != OBJECTIVE REPLACEMENT

RESTORED STATE != AY APPROVAL

RESTORED STATE != EX AUTHORIZATION

RECOVERY READY != RECOVERY EXECUTED

ROLLBACK READY != ROLLBACK EXECUTED
