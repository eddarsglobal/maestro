# MAESTRO Technology Landscape Change Constitution

## Scope

This constitution governs BMF-018:

> MAESTRO can discover evidence that the external technology landscape changed.

The boundary is passive, evidence-first, deterministic, and non-authoritative.

## TLC-01 — External evidence remains evidence

Technology landscape observations originate from externally researched evidence.

External evidence SHALL remain explicitly unverified until the proper verification authority acts.

CHANGE DETECTION != SYSTEM TRUTH.

## TLC-02 — Landscape state is canonicalized before comparison

Observed external technology state SHALL be normalized into deterministic, canonical snapshot state before comparison.

Observation ordering, dictionary ordering, and evidence identifier churn SHALL NOT fabricate a technology landscape change.

## TLC-03 — Snapshot identity represents landscape state

A TechnologyLandscapeSnapshot SHALL identify the declared landscape state for one scope.

Snapshot identity SHALL depend on comparable landscape state, not on incidental evidence identifiers or observation ordering.

## TLC-04 — Comparison is prior versus current

Landscape change detection SHALL compare a prior snapshot with a current snapshot for the same scope.

Snapshots from different scopes SHALL fail closed.

## TLC-05 — CHANGED, UNCHANGED and UNKNOWN are distinct

The detector SHALL represent exactly three semantic outcomes:

- CHANGED
- UNCHANGED
- UNKNOWN

UNKNOWN SHALL NEVER be treated as UNCHANGED.

Missing baseline evidence, missing current evidence, or incomplete comparable evidence SHALL produce UNKNOWN.

## TLC-06 — Change delta is explicit and deterministic

CHANGED SHALL identify explicit deterministic subject deltas:

- added subjects
- removed subjects
- modified subjects

CHANGED SHALL NOT exist without an actual delta.

UNCHANGED and UNKNOWN SHALL NOT carry fabricated deltas.

## TLC-07 — Evidence changes alone do not imply landscape changes

Different evidence IDs, source references, claims, or repeated observations SHALL NOT by themselves imply a landscape change when the canonical observed technology state remains equal.

## TLC-08 — Change evidence carries no downstream authority

TechnologyLandscapeChange SHALL remain passive evidence.

CHANGE DETECTED != UPDATE REQUIRED
CHANGE DETECTED != CAPABILITY CANDIDATE
CHANGE DETECTED != TRUST
CHANGE DETECTED != INSTALL
CHANGE DETECTED != ACTIVATE
CHANGE DETECTED != AUTHORIZE
CHANGE DETECTED != EXECUTE
CHANGE DETECTED != CORE MUTATION
CHANGE DETECTED != SYSTEM TRUTH

Any attempted authority escalation SHALL fail closed.

## TLC-09 — BMF-018 remains separate from BMF-019

BMF-018 detects evidence that the external technology landscape changed.

BMF-019 may later derive governed capability candidates from newly researched technologies.

BMF-018 SHALL NOT create capability candidates, ResearchRequests, provider routing, installation proposals, activation decisions, or execution decisions.

## TLC-10 — The detector is passive and technology-generic

The landscape-change detector SHALL perform no network access, process launch, installation, activation, execution, promotion, learning, provider invocation, or Core mutation.

Current provider, model, runtime, hardware, protocol, and operating-system names SHALL remain external observation data rather than constitutional identities.

## Canonical boundary

```text
EXTERNAL RESEARCH EVIDENCE
          ↓
TechnologyLandscapeObservation
          ↓
TechnologyLandscapeSnapshot
          ↓
PRIOR + CURRENT
          ↓
TechnologyLandscapeChangeDetector
          ↓
CHANGED | UNCHANGED | UNKNOWN
```

## Final invariant

> MAESTRO MAY DETECT THAT THE EXTERNAL TECHNOLOGY LANDSCAPE CHANGED WITHOUT CLAIMING WHAT SHOULD BE DONE ABOUT THAT CHANGE.
