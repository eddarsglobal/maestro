# MAESTRO Governed Failure Containment & Recovery Constitution

## Scope

This constitution governs BMF-028:

Governed updates support failure containment, rollback and recovery.

FCR0.1 is a passive, deterministic, evidence-bound decision boundary.

Existing execution engines remain downstream governed mechanisms.

FCR0.1 does not execute containment, rollback, recovery, activation or release.

## FCR-01 — Recovery context and lineage are explicit

Every assessment SHALL bind an explicit update/recovery context containing:

- subject identity
- update generation identity
- current-state identity
- last-known-good-state identity
- preservation requirements

Failure and recovery evidence SHALL bind the exact context identity.

Evidence SHALL NOT be silently rebound across contexts.

CURRENT STATE != LAST-KNOWN-GOOD STATE merely by assumption.

SOURCE STATE != RECOVERY COPY.

RECOVERY CONTEXT != CORE IDENTITY.

## FCR-02 — Failure and state integrity are separate evidence

Failure detection and current-state integrity SHALL remain independent evidence.

FAILED UPDATE != CORRUPTED USER STATE.

FAILURE DETECTED != STATE LOSS.

NO FAILURE DETECTED != SYSTEM TRUTH.

UNKNOWN FAILURE != HEALTHY.

UNKNOWN INTEGRITY != HEALTHY.

FCR SHALL NOT infer corruption solely from an update failure.

## FCR-03 — Containment precedes destructive recovery decisions

A detected failure that is not yet contained SHALL NOT silently proceed to rollback or recovery.

If containment is explicitly available but not confirmed, the result SHALL be CONTAINMENT_REQUIRED.

Unknown containment evidence SHALL remain UNKNOWN.

Explicit inability to contain a detected failure SHALL fail closed.

CONTAINMENT != DELETION.

CONTAINMENT POSSIBLE != CONTAINMENT EXECUTED.

FAILURE DETECTED != RECOVERY AUTHORIZED.

## FCR-04 — Rollback and recovery are evidence-derived

A contained failure with intact current-state integrity MAY require rollback when:

- rollback path evidence is PASS;
- every rollback preservation requirement is PASS.

A contained failure with explicitly failed current-state integrity SHALL use recovery evidence rather than infer safe rollback.

Recovery MAY be required only when:

- an explicit recovery path exists;
- every recovery preservation requirement is PASS.

ROLLBACK POSSIBLE != ROLLBACK AUTHORIZED.

RECOVERY POSSIBLE != RECOVERY AUTHORIZED.

CHECKPOINT EXISTS != SAFE RECOVERY.

ROLLBACK REFERENCE EXISTS != SAFE ROLLBACK.

## FCR-05 — Assessment outcomes are explicit

FCR0.1 SHALL produce only:

- HEALTHY
- CONTAINMENT_REQUIRED
- ROLLBACK_REQUIRED
- RECOVERY_REQUIRED
- UNRECOVERABLE
- UNKNOWN

HEALTHY requires explicit no-failure evidence and PASS state-integrity evidence.

UNKNOWN evidence SHALL NOT be promoted into rollback or recovery requirements.

Explicitly unavailable preserving recovery SHALL yield UNRECOVERABLE.

UNKNOWN != UNRECOVERABLE.

UNKNOWN != HEALTHY.

UNKNOWN != AUTHORIZED.

## FCR-06 — Preservation is mandatory

Rollback and recovery preservation evidence SHALL cover exactly every declared context preservation requirement.

Rollback preservation and recovery preservation SHALL remain independent.

ROLLBACK SUCCESS != PRESERVATION PROVEN.

RECOVERY SUCCESS != PRESERVATION PROVEN.

STATE TRANSFORMATION != STATE LOSS.

MISSING PRESERVATION EVIDENCE != PASS.

UNKNOWN PRESERVATION != PASS.

## FCR-07 — Response plans are passive

Containment plans SHALL require CONTAINMENT_REQUIRED.

Rollback plans SHALL require ROLLBACK_REQUIRED.

Recovery plans SHALL require RECOVERY_REQUIRED.

Plan steps SHALL be explicit, ordered from 1 and use unique step identities.

Rollback/recovery plans SHALL bind the declared last-known-good state.

A plan grants no authority.

ROLLBACK PLAN != ROLLBACK EXECUTION.

RECOVERY PLAN != RECOVERY EXECUTION.

CONTAINMENT PLAN != CONTAINMENT EXECUTION.

PLAN CREATED != STATE MUTATED.

## FCR-08 — Existing AY/EX authority remains downstream

FCR0.1 SHALL NOT replace existing authority-aware rollback or recovery bridges.

Existing governed runtime mechanisms MAY consume FCR evidence through explicit downstream bridges.

Fresh AY acknowledgement and EX authorization requirements remain owned by their existing governed execution boundaries.

FCR assessment SHALL NOT fabricate AY acknowledgement.

FCR assessment SHALL NOT fabricate EX authorization.

RECOVERY EVIDENCE != RECOVERY AUTHORITY.

ROLLBACK EVIDENCE != ROLLBACK AUTHORITY.

## FCR-09 — FCR grants no operational authority

Neither assessment nor planning SHALL assert:

- containment authorization
- containment execution
- rollback authorization
- rollback execution
- recovery authorization
- recovery execution
- activation authorization
- release authorization
- source-state mutation
- source-state deletion
- system truth

Authority escalation SHALL fail closed.

RECOVERY SUCCESS != ACTIVATION AUTHORIZED.

ROLLBACK SUCCESS != RELEASE AUTHORIZED.

RECOVERY EVIDENCE != SYSTEM TRUTH.

## FCR-10 — BMF-028 closes recovery governance without merging BMF-027

BMF-027 governs durable-state compatibility and passive migration planning.

BMF-028 governs failure containment, rollback and recovery assessment/planning.

BMF-028 != BMF-027.

MIGRATION PLAN != RECOVERY PLAN.

MIGRATION EXECUTION != RECOVERY EXECUTION.

FCR0.1 SHALL perform no network access, persistence mutation, filesystem mutation, rollback execution, recovery execution, activation, deployment, publication, installation or Core mutation.

Existing recovery, checkpoint, transaction, rollback and activation engines are downstream mechanisms, not constitutional dependencies of FCR0.1.

## Canonical boundary

UPDATE / STATE CONTEXT
        +
FAILURE EVIDENCE
        +
CURRENT-STATE INTEGRITY
        +
CONTAINMENT EVIDENCE
        +
ROLLBACK PATH EVIDENCE
        +
RECOVERY PATH EVIDENCE
        +
PRESERVATION EVIDENCE
        |
        v
GOVERNED RECOVERY ASSESSMENT
        |
        +---- HEALTHY
        |
        +---- CONTAINMENT_REQUIRED
        |           |
        |           v
        |     PASSIVE CONTAINMENT PLAN
        |
        +---- ROLLBACK_REQUIRED
        |           |
        |           v
        |       PASSIVE ROLLBACK PLAN
        |
        +---- RECOVERY_REQUIRED
        |           |
        |           v
        |       PASSIVE RECOVERY PLAN
        |
        +---- UNRECOVERABLE
        |
        +---- UNKNOWN

The boundary stops before operational authority or execution.

## Constitutional separations

FAILURE DETECTED != RECOVERY AUTHORIZED

RECOVERY POSSIBLE != RECOVERY AUTHORIZED

ROLLBACK POSSIBLE != ROLLBACK AUTHORIZED

ROLLBACK PLAN != ROLLBACK EXECUTION

RECOVERY PLAN != RECOVERY EXECUTION

CONTAINMENT != DELETION

FAILED UPDATE != CORRUPTED USER STATE

RECOVERY SUCCESS != ACTIVATION AUTHORIZED

ROLLBACK SUCCESS != RELEASE AUTHORIZED

RECOVERY EVIDENCE != SYSTEM TRUTH

SOURCE STATE != RECOVERY COPY

BMF-028 != BMF-027

## Final invariant

MAESTRO MAY ASSESS FAILURE CONTAINMENT, ROLLBACK AND RECOVERY REQUIREMENTS AND PRODUCE PASSIVE RESPONSE PLANS ONLY FROM EXPLICIT CONTEXT-BOUND EVIDENCE AND COMPLETE PRESERVATION EVIDENCE, WITHOUT TURNING RECOVERY EVIDENCE OR PLANNING INTO EXECUTION, ACTIVATION, RELEASE OR STATE-MUTATION AUTHORITY.
