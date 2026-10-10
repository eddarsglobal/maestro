# MAESTRO Governed Durable State Compatibility Constitution

## Scope

This constitution governs BMF-027:

Update generations define governed compatibility and migration for durable user state.

DCM0.1 provides a passive, deterministic and evidence-bound boundary for compatibility assessment and migration planning.

It does not execute migrations.

It does not mutate durable state.

It does not authorize activation.

It does not authorize rollback.

It does not mutate Core.

## DCM-01 — Durable state lineage is explicit

Compatibility SHALL be evaluated between explicit source and target durable-state descriptors.

Each descriptor SHALL bind:

- durable-state identity
- durable-state type
- update generation identity
- application version
- schema identity
- schema version
- format identity
- format version
- preservation requirements

Source and target SHALL describe the same durable-state identity and durable-state type.

Evidence SHALL be explicitly bound to the source descriptor identity and target descriptor identity.

Evidence SHALL NOT be silently rebound to another source or target generation.

USER STATE != CORE STATE.

STATE IDENTITY != APPLICATION IDENTITY.

GENERATION IDENTITY != SCHEMA IDENTITY.

## DCM-02 — Versions are opaque evidence coordinates

Application versions, schema versions and format versions are opaque identifiers.

DCM0.1 SHALL NOT infer compatibility, incompatibility, ordering, migration need, or migration safety from version numbering alone.

VERSION CHANGE != MIGRATION REQUIRED.

SCHEMA VERSION != APPLICATION VERSION.

FORMAT VERSION != APPLICATION VERSION.

NEWER VERSION != COMPATIBLE.

OLDER VERSION != INCOMPATIBLE.

Version labels MAY differ while states remain compatible.

COMPATIBLE != IDENTICAL.

## DCM-03 — Compatibility is directional

Backward compatibility and forward compatibility SHALL be represented independently.

Target ability to consume source state SHALL NOT imply source ability to consume target state.

FORWARD COMPATIBLE != BACKWARD COMPATIBLE.

Compatibility SHALL separately preserve evidence for reading and writing.

READABLE != WRITABLE.

READ SUCCESS != WRITE SAFETY.

A state that can be read but cannot be safely written SHALL NOT be treated as fully directionally compatible.

## DCM-04 — Preservation requirements are mandatory

Every durable state descriptor SHALL declare at least one explicit preservation requirement.

Compatibility evidence SHALL cover exactly the union of source and target preservation requirements.

A preservation requirement introduced by the target generation SHALL NOT be silently omitted.

Direct compatibility and migration compatibility SHALL carry independent preservation evidence.

STATE TRANSFORMATION != STATE LOSS.

TRANSFORMABLE != PRESERVED.

MISSING PRESERVATION EVIDENCE != PRESERVED.

UNKNOWN PRESERVATION != PASS.

## DCM-05 — Compatibility has four governed outcomes

A governed compatibility assessment SHALL resolve only to:

- COMPATIBLE
- MIGRATION_REQUIRED
- INCOMPATIBLE
- UNKNOWN

COMPATIBLE requires sufficient direct read, write and preservation evidence.

MIGRATION_REQUIRED requires direct incompatibility together with an explicit available migration path and successful migration-preservation evidence.

INCOMPATIBLE represents an explicit failure for which no preserving migration path is available or preservation explicitly fails.

UNKNOWN represents insufficient evidence.

UNKNOWN COMPATIBILITY != COMPATIBLE.

UNKNOWN COMPATIBILITY != MIGRATION_REQUIRED.

UNKNOWN != FAILURE.

UNKNOWN != PASS.

A known migration path SHALL NOT convert unknown direct compatibility into a migration requirement.

## DCM-06 — Migration requirement is evidence-derived

Migration SHALL NOT be required merely because:

- an application version changed
- a schema version changed
- a format version changed
- a generation identity changed

A MIGRATION_REQUIRED assessment SHALL require:

1. explicit evidence that direct compatibility is insufficient;
2. an explicit migration path marked available;
3. explicit PASS evidence for every migration preservation requirement.

MIGRATION POSSIBLE != MIGRATION REQUIRED.

MIGRATION REQUIRED != MIGRATION AUTHORIZED.

MIGRATION POSSIBLE != MIGRATION AUTHORIZED.

UNKNOWN MIGRATION PATH != MIGRATION REQUIRED.

## DCM-07 — Migration plans are passive

A migration plan MAY be created only from a MIGRATION_REQUIRED assessment.

No migration plan SHALL be created from:

- COMPATIBLE
- UNKNOWN
- INCOMPATIBLE

Migration plan steps SHALL:

- be explicit
- be ordered
- use contiguous ordinals starting at 1
- use unique step identities
- remain descriptive and passive

A migration plan MAY reference rollback evidence.

A rollback reference grants no rollback authority.

MIGRATION PLAN != MIGRATION EXECUTION.

PLAN CREATED != STATE MUTATED.

ROLLBACK POSSIBLE != ROLLBACK AUTHORIZED.

## DCM-08 — Compatibility lineage is deterministic

Equivalent descriptor content SHALL produce equivalent descriptor identity.

Equivalent evidence content SHALL produce equivalent evidence identity.

Equivalent assessment content SHALL produce equivalent assessment identity.

Ordering of preservation requirements or preservation evidence SHALL NOT alter semantic identity.

Evidence SHALL remain cryptographically/content-bound to its declared source and target descriptors.

CROSS-LINEAGE REBINDING SHALL FAIL CLOSED.

DETERMINISTIC != AUTHORIZED.

CONTENT IDENTITY != SYSTEM TRUTH.

## DCM-09 — DCM grants no operational authority

Neither compatibility assessment nor migration planning SHALL assert:

- migration authorization
- migration execution
- activation authorization
- rollback authorization
- source-state mutation
- source-state deletion
- Core mutation
- acceptance of state loss
- system truth

Any attempt to assert these authorities inside DCM0.1 SHALL fail closed.

MIGRATION SUCCESS != ACTIVATION AUTHORIZED.

MIGRATION EVIDENCE != MIGRATION AUTHORITY.

COMPATIBILITY RESULT != ACTIVATION AUTHORITY.

STATE COMPATIBILITY != STATE MUTATION AUTHORITY.

## DCM-10 — BMF-027 remains passive and separate from recovery

DCM0.1 SHALL perform no:

- network access
- database mutation
- filesystem state mutation
- migration execution
- restore execution
- rollback execution
- installation
- activation
- deployment
- deletion
- Core mutation

DCM0.1 evaluates supplied evidence and may produce a passive migration plan only.

Existing storage engines, migration executors, recovery engines, rollback engines or activation systems MAY provide evidence or consume downstream governed decisions through explicit bridges.

They SHALL NOT become constitutional dependencies of DCM0.1.

BMF-027 governs compatibility and passive migration planning.

BMF-028 governs failure containment, rollback and recovery.

BMF-027 != BMF-028.

MIGRATION PLAN != RECOVERY EXECUTION.

ROLLBACK CAPABILITY != ROLLBACK AUTHORIZATION.

## Canonical boundary

SOURCE UPDATE GENERATION
        +
SOURCE DURABLE-STATE DESCRIPTOR
        |
        | explicit evidence binding
        v
TARGET UPDATE GENERATION
        +
TARGET DURABLE-STATE DESCRIPTOR
        |
        v
READ EVIDENCE
+
WRITE EVIDENCE
+
BACKWARD / FORWARD EVIDENCE
+
PRESERVATION EVIDENCE
+
MIGRATION-PATH EVIDENCE
+
ROLLBACK-PATH EVIDENCE
        |
        v
GOVERNED COMPATIBILITY ASSESSMENT
        |
        +---- COMPATIBLE
        |
        +---- MIGRATION_REQUIRED
        |          |
        |          v
        |     PASSIVE MIGRATION PLAN
        |
        +---- INCOMPATIBLE
        |
        +---- UNKNOWN

The boundary stops before:

- migration execution
- durable-state mutation
- source-state deletion
- activation
- rollback execution
- rollback authorization
- Core mutation
- acceptance of state loss
- system-truth assertion

## Constitutional separations

VERSION CHANGE != MIGRATION REQUIRED

COMPATIBLE != IDENTICAL

READABLE != WRITABLE

MIGRATION POSSIBLE != MIGRATION AUTHORIZED

MIGRATION PLAN != MIGRATION EXECUTION

USER STATE != CORE STATE

STATE TRANSFORMATION != STATE LOSS

UNKNOWN COMPATIBILITY != COMPATIBLE

FORWARD COMPATIBLE != BACKWARD COMPATIBLE

MIGRATION SUCCESS != ACTIVATION AUTHORIZED

SCHEMA VERSION != APPLICATION VERSION

ROLLBACK POSSIBLE != ROLLBACK AUTHORIZED

## Final invariant

MAESTRO MAY ASSESS DURABLE USER-STATE COMPATIBILITY AND PRODUCE A PASSIVE MIGRATION PLAN ONLY FROM EXPLICIT SOURCE/TARGET LINEAGE, DIRECTIONAL READ/WRITE EVIDENCE AND COMPLETE PRESERVATION EVIDENCE, WITHOUT TURNING COMPATIBILITY OR MIGRATION PLANNING INTO STATE-MUTATION, ACTIVATION OR ROLLBACK AUTHORITY.
