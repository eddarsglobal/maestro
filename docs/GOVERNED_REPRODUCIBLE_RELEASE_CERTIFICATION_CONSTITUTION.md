# MAESTRO Governed Reproducible Release Certification Constitution

## Scope

This constitution governs BMF-024:

Reproducible release gates certify supported platforms without changing Core constitutional meaning.

RRC0.1 creates a passive, deterministic and evidence-bound release certification boundary.

It certifies evidence.

It does not publish, deploy, push, activate, install, authorize, mutate tags, or mutate Core.

## RRC-01 — Supported platforms are explicit

Every release manifest SHALL contain an explicit non-empty set of supported platform identities.

Supported platform identities are release data.

They are not constitutional identities.

Duplicate supported platform identities SHALL fail closed.

No platform SHALL become supported merely because evidence for it exists.

PLATFORM OBSERVED != PLATFORM SUPPORTED.

PLATFORM PASS != UNIVERSAL SUPPORT.

## RRC-02 — Release identity binds immutable Core identity

Every release manifest SHALL bind:

- release identity
- release version
- Core source SHA-256 digest
- Core constitutional fingerprint
- supported platform set
- build recipe identity

Core source digest and constitutional fingerprint are mandatory.

Missing Core identity SHALL fail closed.

RELEASE IDENTITY != CORE IDENTITY.

PACKAGING IDENTITY != CONSTITUTIONAL IDENTITY.

## RRC-03 — Per-platform evidence is explicit

Every supported platform certification SHALL preserve explicit evidence for:

- platform identity
- build gate state
- test gate state
- artifact identity
- artifact digest
- reproduced artifact digest
- Core source digest
- constitutional fingerprint
- evidence source reference

Gate evidence SHALL use explicit PASS, FAIL or UNKNOWN states.

UNKNOWN != PASS.

BUILD SUCCESS != RELEASE CERTIFIED.

## RRC-04 — Reproducibility is evidence-bound

A platform SHALL NOT pass reproducible release certification unless both the original artifact digest and reproduced artifact digest are present and equal.

A missing artifact digest SHALL produce INCOMPLETE evidence.

A digest mismatch SHALL produce FAILED evidence.

ARTIFACT HASH MATCH != TRUSTED.

REPRODUCIBLE != TRUSTED.

REPRODUCIBLE != RELEASE AUTHORIZED.

## RRC-05 — Core meaning must remain invariant

Every platform certification SHALL bind to the same Core source digest and the same constitutional fingerprint declared by the release manifest.

A Core source mismatch SHALL fail.

A constitutional fingerprint mismatch SHALL fail.

Platform-specific packaging MAY differ while constitutional meaning remains identical.

CERTIFIED PLATFORM != CORE SEMANTIC VARIANT.

PACKAGING DIFFERENCE != CONSTITUTIONAL DIFFERENCE.

PLATFORM DIFFERENCE != CONSTITUTIONAL DIFFERENCE.

## RRC-06 — Platform certification is fail-closed

A platform certification SHALL be:

- FAILED when any explicit failure exists
- INCOMPLETE when no explicit failure exists but required evidence is missing or UNKNOWN
- PASS only when every required gate and reproducibility condition is satisfied

FAILED takes state precedence over INCOMPLETE.

All observed failure and incompleteness reasons SHALL remain preserved even when FAILED determines the final state.

FAILURE STATE != LOSS OF INCOMPLETE EVIDENCE.

UNKNOWN != ZERO.

UNKNOWN != PASS.

## RRC-07 — Release certification requires the complete supported set

A release SHALL NOT receive PASS unless every platform declared in the manifest's supported platform set has exactly one governed platform certification and every such certification is PASS.

Missing supported platforms SHALL produce INCOMPLETE unless another platform has explicitly FAILED.

A FAILED supported platform SHALL make the release FAILED.

One passing platform SHALL never imply release-wide PASS.

ONE PLATFORM PASS != ALL SUPPORTED PLATFORMS PASS.

PARTIAL PLATFORM COVERAGE != RELEASE PASS.

SUPPORTED SET COMPLETE + ALL PASS is required for PASS.

## RRC-08 — Certification lineage is deterministic and manifest-bound

Platform certifications SHALL remain bound to exactly one release manifest.

Cross-manifest certification reuse SHALL fail closed.

Duplicate platform certifications SHALL fail closed.

Equivalent release evidence SHALL produce deterministic manifest, platform certification and release certification identities independent of input ordering.

CERTIFICATION IDENTITY != AUTHORIZATION.

DETERMINISTIC != AUTHORIZED.

## RRC-09 — Certification grants no release authority

Neither platform PASS nor release PASS SHALL assert:

- trust
- release authorization
- publish authorization
- deploy authorization
- tag mutation authorization
- Core mutation
- universal platform support
- system truth

Any such authority escalation inside RRC0.1 SHALL fail closed.

RELEASE EVIDENCE != RELEASE AUTHORIZATION.

RELEASE CERTIFIED != RELEASE AUTHORIZED.

PASS != PUBLISH AUTHORIZED.

PASS != DEPLOY AUTHORIZED.

PASS != TAG MUTATION AUTHORIZED.

## RRC-10 — BMF-024 remains passive and constitution-preserving

RRC0.1 SHALL perform no:

- network access
- provider execution
- subprocess execution
- artifact publication
- deployment
- repository push
- tag creation or movement
- installation
- activation
- promotion
- Core mutation

RRC0.1 SHALL evaluate supplied evidence only.

Existing CI systems, build systems, packaging systems, Genesis release gates and platform-specific tooling MAY provide evidence through explicit governed bridges.

They SHALL NOT become constitutional dependencies of RRC0.1.

RELEASE GATE != CORE MUTATION.

CI GREEN != RELEASE AUTHORIZED.

BUILD SUCCESS != RELEASE CERTIFIED.

## Canonical boundary

RELEASE IDENTITY
        +
IMMUTABLE CORE SOURCE IDENTITY
        +
CORE CONSTITUTIONAL FINGERPRINT
        +
EXPLICIT SUPPORTED PLATFORM SET
        +
BUILD RECIPE IDENTITY
        |
        v
PER-PLATFORM GATE EVIDENCE
        +
ARTIFACT DIGEST
        +
REPRODUCED ARTIFACT DIGEST
        |
        v
PLATFORM CERTIFICATION
        |
        +---- PASS
        +---- FAILED
        +---- INCOMPLETE
        |
        v
COMPLETE SUPPORTED-PLATFORM SET
        |
        v
RELEASE CERTIFICATION EVIDENCE
        |
        +---- PASS
        +---- FAILED
        +---- INCOMPLETE

The boundary stops before release authorization, publication, deployment, tag mutation, installation, activation, trust, universal-support assertion, or Core mutation.

## Final invariant

MAESTRO MAY CERTIFY REPRODUCIBLE RELEASE EVIDENCE ACROSS AN EXPLICIT SET OF SUPPORTED PLATFORMS ONLY WHEN EVERY PLATFORM IS BOUND TO THE SAME CORE SOURCE AND CONSTITUTIONAL MEANING, WITHOUT TURNING CERTIFICATION INTO RELEASE AUTHORITY.
