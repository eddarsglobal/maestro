# MAESTRO v1.1.0 — Governed Policy Activation

## Doctrine

PROMOTION EVIDENCE IS NOT ACTIVATION AUTHORITY.

NO POLICY BECOMES ACTIVE WITHOUT GOVERNANCE, OBSERVABILITY AND ROLLBACK.

The activation control plane is deterministic. Models, Outcome Intelligence,
Academy, and domain Councils may provide evidence or recommendations, but they
cannot grant themselves activation authority.

## Lifecycle

PROMOTION_READY -> ACTIVATION_PROPOSED -> AY_VALIDATED -> EX_AUTHORIZED
-> CANARY -> CANARY_VERIFIED -> ACTIVE

Safety exits:

- AY FAUTE -> BLOCKED
- EX denial -> BLOCKED
- degraded CANARY -> ROLLED_BACK
- runtime degradation after activation -> governed rollback

## Constitutional laws

1. APTE-GPA-01 — Promotion evidence is not activation authority.
2. APTE-GPA-02 — PROMOTION_READY is required before activation proposal.
3. APTE-GPA-03 — AY validation is required before EX authorization.
4. APTE-GPA-04 — Only EX control-plane authority may authorize activation.
5. APTE-GPA-05 — Activation contracts are immutable.
6. APTE-GPA-06 — CANARY precedes ACTIVE.
7. APTE-GPA-07 — Runtime evidence is required for CANARY verification.
8. APTE-GPA-08 — Rollback must exist before CANARY.
9. APTE-GPA-09 — Activation lifecycle must survive restart.
10. APTE-GPA-10 — Models may recommend but may not authorize activation.

## Adaptive runtime bridge

The GPA control plane does not replace the existing `AdaptivePolicyManager`.

The manager remains responsible for executing the concrete adaptive policy
transition. GPA controls when that call becomes legal.

The bridge requires:

- GPA state is `CANARY_VERIFIED`;
- AY validation is present;
- EX authorization is present;
- `PromotionEvidence.learning_candidate_id` matches the activation contract;
- the referenced policy already exists in the adaptive runtime.

Only after `AdaptivePolicyManager.activate(...)` succeeds may GPA persist
`ACTIVE`.

> APTE-GPA-11 - ADAPTIVE RUNTIME ACTIVATION REQUIRES CANARY_VERIFIED GPA STATE.

## Runtime rollback governance

Activation authorization and rollback authorization are separate governance
events.

An ACTIVE policy may be rolled back through the adaptive runtime only when:

- runtime degradation has an evidence reference;
- AY explicitly acknowledges the rollback condition;
- EX explicitly authorizes rollback;
- a rollback reason is recorded;
- `AdaptivePolicyManager.rollback(...)` succeeds.

GPA persists `ROLLED_BACK` only after the adaptive runtime rollback succeeds.

> APTE-GPA-12 - RUNTIME ROLLBACK REQUIRES FRESH AY ACKNOWLEDGEMENT AND EX AUTHORIZATION.

## OGA candidate provenance binding

Production activation must not trust a caller-provided `PROMOTION_READY` label
by itself.

When GPA is composed by `ProductionGenesisSystem`, it is bound to the durable
Outcome-Governed Adaptation candidate ledger. Before creating an activation
contract, GPA verifies:

- the candidate ID exists exactly once in the current OGA projection;
- the persisted candidate is `PROMOTION_READY`;
- task family matches;
- proposed change matches exactly;
- candidate key matches when present.

A fabricated or stale candidate object therefore cannot open a production
activation contract.

> APTE-GPA-13 - PRODUCTION ACTIVATION REQUIRES PERSISTED OGA CANDIDATE PROVENANCE.

## LEARNING-GRADE EVALUATION PROVENANCE

A persisted `PROMOTION_READY` label is insufficient by itself. Production GPA
also requires OGA metadata proving that promotion came from a learning-grade
deterministic evaluation profile.

This blocks legacy, stochastic, diagnostic, or manually checkpointed promotion
evidence from crossing the activation boundary.

## Deep immutability and canonical integrity

A frozen dataclass is insufficient when it contains mutable nested structures.

Activation contracts and canary evidence therefore deep-freeze their metadata.
Contract identity is recomputed from canonical JSON-compatible content and is
asserted again at sensitive activation boundaries.

Snapshot metadata remains mutable because it represents governed lifecycle
state; immutable contract/evidence payloads do not.

> APTE-GPA-14 - ACTIVATION CONTRACT AND CANARY EVIDENCE METADATA ARE DEEPLY IMMUTABLE.

## Contract-bound governance attestations

Production AY/EX decisions are no longer represented only by free actor
strings, booleans, or unbound references.

The strict production GPA engine requires deterministic attestations bound to
the immutable activation contract, exact governance action, decision, evidence
references and, where applicable, the parent authority attestation.

EX activation authorization is chained to the preceding AY validation.
Runtime rollback requires fresh AY acknowledgement and EX authorization bound
to the rollback reason and degradation evidence.

Attestation IDs are content-addressed SHA-256 integrity references. They are
provenance bindings, not secret-key identity signatures.

The legacy GPA engine remains available for low-level backwards-compatible
tests. ProductionGenesisSystem uses StrictGovernedPolicyActivation.

> APTE-GPA-15 - PRODUCTION AY/EX AUTHORITY REQUIRES CONTRACT-BOUND CHAINED ATTESTATIONS.

## Persistent adaptive policy control plane

An adaptive policy activation is not durable if the active policy pointer,
policy statuses, and activation history exist only in process memory.

MAESTRO therefore provides a persistent adaptive policy manager that stores:

- the complete policy set;
- each policy status and version;
- active policy pointers by policy kind;
- activation and rollback history.

The state is written as one atomic snapshot using write + fsync + replace.
Restart reconstruction validates that every active pointer references an
existing ACTIVE policy of the same kind and that no orphan ACTIVE policy exists.

This persistence layer does not itself solve the cross-component GPA/manager
transaction. It establishes the durable participant required for the next
transaction-journal hardening step.

> APTE-GPA-16 - ACTIVE ADAPTIVE POLICY STATE MUST SURVIVE PROCESS RESTART.

## Durable manager/GPA commit transaction

Production activation and rollback span two durable participants:

1. PersistentAdaptivePolicyManager;
2. GPA activation lifecycle ledger.

Strict GPA coordinates them with an append-only fsync-backed journal:

`PREPARED -> MANAGER_COMMITTED -> GPA_COMMITTED`

Recovery rules:

- PREPARED + manager at BEFORE -> ABORTED;
- PREPARED + manager at AFTER -> MANAGER_COMMITTED;
- MANAGER_COMMITTED + GPA at BEFORE -> finish GPA commit;
- MANAGER_COMMITTED + GPA at AFTER -> finalize journal;
- any state matching neither BEFORE nor AFTER -> BLOCKED.

Production runtime activation/rollback rejects the ephemeral
AdaptivePolicyManager.

The GPA ledger checkpoint is fsync-durable before a transaction may become
GPA_COMMITTED.

> APTE-GPA-17 - PRODUCTION MANAGER/GPA COMMITS REQUIRE DURABLE TRANSACTION JOURNAL AND RECOVERY.

## Production Genesis durable adaptive ownership

A recovery mechanism is not a production guarantee unless the production
composition root owns the durable participants and invokes reconciliation
before declaring the runtime READY.

ProductionGenesisSystem therefore owns:

- one PersistentAdaptivePolicyManager;
- one AdaptiveController bound to that exact manager;
- one StrictGovernedPolicyActivation control plane;
- one durable GPA runtime transaction journal.

At startup, Genesis validates the core boot contract, reconciles pending
runtime transactions against the persistent manager and GPA ledger, then
checks for any durable BLOCKED transaction.

A durable BLOCKED transaction is fail-closed: ProductionGenesisSystem must not
report READY until the conflict is explicitly resolved by a governed recovery
procedure.

> APTE-GPA-18 - PRODUCTION GENESIS MUST OWN THE DURABLE ADAPTIVE CONTROL PLANE AND RECOVER BEFORE READY.

## Candidate-to-contract lineage uniqueness

A persisted OGA candidate represents one governed adaptation proposition.
It may not be rebound to multiple activation contracts with different
policy targets, baselines, rollback targets, canary fractions, or metadata.

GPA therefore indexes persisted activation lifecycles by both contract ID and
candidate ID.

Reproposing the exact same contract is idempotent and returns the latest
persisted snapshot for that contract.

Reproposing the same candidate with any contract-changing field is a lineage
conflict and is rejected before a second PROPOSED snapshot can be persisted.

The rule survives restart because lineage is derived from the durable
activation ledger.

> APTE-GPA-19 - ONE OGA CANDIDATE MAY OPEN ONLY ONE GPA CONTRACT LINEAGE.

## Runtime transaction journal integrity

Every runtime transaction event is content-addressed with a deterministic
SHA-256 `event_id` over its canonical complete payload.

Each appended event stores `previous_event_id`, linking it to the immediately
preceding durable journal event.

Journal load validates both event integrity and chain continuity. Modification,
interior deletion, or reordering fails closed before recovery executes.

Governance payloads are deep immutable in memory and thaw to ordinary JSON
only for persistence.

These hashes provide deterministic integrity and corruption detection; they
are not secret-key authentication signatures.

> APTE-GPA-20 - RUNTIME TRANSACTION EVENTS MUST BE CONTENT-ADDRESSED AND HASH-CHAINED.

