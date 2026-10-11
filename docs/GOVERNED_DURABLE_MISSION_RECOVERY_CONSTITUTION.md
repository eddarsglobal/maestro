# MAESTRO Governed Durable Mission Recovery Constitution

## Scope

DMR0.1 governs:

- BM2-022 Durable Mission
- BM2-023 Autonomous Recovery

It extends durable recovery to the Phase 2 mission surface while preserving
existing checkpoint, FCR, DCM, AY, EX and TX authority boundaries.

## DMR-01 — Durable state is broader than the legacy runtime checkpoint

A governed Phase 2 durable mission checkpoint SHALL preserve:

- canonical mission snapshot
- mission contract
- governed mission plan
- DAG dependencies
- execution routing
- selected resources
- execution waves
- worker placements
- idempotency keys
- node execution evidence
- provenance references
- node closure state
- mission verdict evidence
- mission verdict artifact
- retry state
- Council runtime state
- recovery information
- binding to the existing runtime checkpoint

MISSION SNAPSHOT != COMPLETE DURABLE MISSION.

## DMR-02 — Existing checkpoint remains bound, not replaced

DMR0.1 SHALL bind the existing runtime checkpoint schema and SHA-256 digest.

It SHALL NOT silently replace the runtime checkpoint or CrossNode recovery
primitives.

PHASE2 CHECKPOINT != LEGACY CHECKPOINT REPLACEMENT.

## DMR-03 — Checkpoint integrity is cryptographic

The Phase 2 durable payload SHALL use canonical serialization and SHA-256.

The outer envelope SHALL itself be checksummed.

Modified payload or envelope data SHALL fail closed.

CHECKPOINT PRESENT != CHECKPOINT INTACT.

HASH MISMATCH != RECOVERABLE STATE.

## DMR-04 — Resume preserves semantic lineage

Checkpoint/resume SHALL preserve exact identities for:

- mission contract
- objective
- governed plan
- routing plan
- nodes
- Councils
- capabilities
- resources
- evidence
- retries
- recovery generation

RESUME != REPLAN.

RESUME != OBJECTIVE CHANGE.

## DMR-05 — Durable persistence grants no operational authority

Creating, saving or loading a durable mission checkpoint SHALL NOT:

- authorize execution
- authorize effects
- authorize durable TX commit
- transition canonical mission state
- authorize learning
- assert system truth

CHECKPOINTED != AUTHORIZED.

RESTORED != EXECUTION AUTHORIZED.

## DMR-06 — Autonomous recovery composes existing FCR evidence

Mission-level autonomous recovery SHALL consume explicit references to
existing FCR assessment/plan evidence.

DMR0.1 SHALL NOT silently reinterpret FCR authority.

FCR PLAN != RECOVERY EXECUTION.

RECOVERY PROPOSAL != RECOVERY EXECUTION.

## DMR-07 — Recovery may deterministically propose containment, rollback or resume

When failure and integrity evidence are complete, DMR0.1 MAY derive:

- CONTAINMENT_PROPOSED
- ROLLBACK_PROPOSED
- RESUME_PROPOSED
- UNRECOVERABLE
- HEALTHY
- UNKNOWN

The derived state SHALL match the existing FCR assessment and action.

AUTONOMOUS DECISION != AUTONOMOUS EXECUTION.

## DMR-08 — Replanning composes adaptive-routing evidence

When prior adaptive routing determines REPLAN_REQUIRED, mission recovery MAY
produce REPLAN_PROPOSED.

Replanning SHALL preserve the checkpointed objective fingerprint.

REPLAN PROPOSED != REPLAN EXECUTED.

REPLAN != OBJECTIVE REPLACEMENT.

## DMR-09 — Recovery cannot bypass AY or EX

Every recovery decision SHALL explicitly require:

- AY revalidation
- EX reauthorization

Workers, models, providers, restored state and checkpoint loaders SHALL NOT
acquire execution authority.

RESTORED STATE != AY APPROVAL.

RESTORED STATE != EX AUTHORIZATION.

## DMR-10 — Recovery remains upstream of canonical mutation

DMR0.1 SHALL NOT:

- call Kernel.close
- transition mission lifecycle state
- execute rollback
- execute recovery
- execute replanning
- execute effects
- authorize TX durable commit
- authorize learning
- assert system truth

Existing runtime/FCR/DCM/AY/EX/TX mechanisms remain downstream.

RECOVERY READY != RECOVERY EXECUTED.

ROLLBACK READY != ROLLBACK EXECUTED.

## Canonical durability boundary

LEGACY RUNTIME CHECKPOINT
        |
        +---- schema
        +---- SHA-256
        |
        v
PHASE 2 DURABLE MISSION
        |
        +---- MISSION
        +---- CONTRACT
        +---- PLAN
        +---- DAG
        +---- ROUTING
        +---- RESOURCES
        +---- IDEMPOTENCY
        +---- EVIDENCE
        +---- PROVENANCE
        +---- RETRIES
        +---- COUNCIL STATE
        +---- VERDICTS
        +---- RECOVERY INFO
        |
        v
CANONICAL SERIALIZATION
        |
        v
SHA-256 PAYLOAD
        |
        v
SHA-256 ENVELOPE
        |
        v
ATOMIC DURABLE STORE
        |
        v
GOVERNED LOAD / RESUME
        |
        v
SAME SEMANTIC FINGERPRINT

## Canonical recovery boundary

DURABLE MISSION CHECKPOINT
        |
        +
CHECKPOINT INTEGRITY
        |
        +
FAILURE EVIDENCE
        |
        +
EXISTING FCR ASSESSMENT / PLAN
        |
        +
ADAPTIVE ROUTING STATE
        |
        v
DETERMINISTIC RECOVERY DECISION
        |
        +---- HEALTHY
        +---- CONTAINMENT_PROPOSED
        +---- ROLLBACK_PROPOSED
        +---- RESUME_PROPOSED
        +---- REPLAN_PROPOSED
        +---- UNRECOVERABLE
        +---- UNKNOWN
        |
        v
AY REVALIDATION REQUIRED
        |
        v
EX REAUTHORIZATION REQUIRED
        |
        v
BOUNDARY STOPS

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

## Final invariant

MAESTRO SHALL PRESERVE THE COMPLETE PHASE 2 MISSION SURFACE ACROSS
GOVERNED CHECKPOINT/RESUME WITH CRYPTOGRAPHIC INTEGRITY AND EXACT
SEMANTIC LINEAGE, AND MAY AUTONOMOUSLY DERIVE A CONTAINMENT,
ROLLBACK, RECOVERY OR REPLAN PROPOSAL FROM EXISTING FCR AND ADAPTIVE
EVIDENCE WITHOUT THE RESTORED STATE OR RECOVERY LAYER ACQUIRING AY,
EX, TX, EFFECT, LEARNING OR CANONICAL MISSION-STATE AUTHORITY.
