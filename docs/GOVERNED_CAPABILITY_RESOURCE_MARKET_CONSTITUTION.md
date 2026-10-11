# MAESTRO Governed Capability Resource Market Constitution

## Scope

CIM0.1 governs:

- BM2-010 Capability Graph
- BM2-011 Intelligence Market
- BM2-012 Model Sovereignty

It connects generic mission capability demand to replaceable
intelligence-resource selection without moving mission authority
into a provider, model or runtime.

## CIM-01 — Capability contracts are technology-neutral

Each mission capability SHALL become a generic capability contract.

Capability contracts SHALL bind mission demand evidence, not
provider/model/runtime identities.

CAPABILITY != PROVIDER.

CAPABILITY != MODEL.

CAPABILITY != RUNTIME.

## CIM-02 — Capability graph identity excludes technology identity

The mission capability graph SHALL be derived entirely from
mission-contract identity, capability-demand identity and generic
capability contracts.

Changing provider, model or runtime SHALL NOT change the capability graph.

TECHNOLOGY IDENTITY != MISSION SEMANTICS.

RESOURCE REPLACEMENT != CAPABILITY CHANGE.

## CIM-03 — Technology references are candidate metadata

Provider, model and runtime references MAY exist on resource candidates
as opaque edge metadata.

They SHALL NOT become constitutional capability identities.

KNOWN TECHNOLOGY != CONSTITUTIONAL DEPENDENCY.

PROVIDER METADATA != PROVIDER AUTHORITY.

MODEL METADATA != MODEL AUTHORITY.

## CIM-04 — Market selection is evidence and policy constrained

A resource MAY be selected only when explicit evidence and policy satisfy:

- required capability
- availability
- evidence quality
- reliability
- privacy
- cost ceiling
- latency ceiling
- locality requirement
- mission-bound constraints

RESOURCE AVAILABLE != RESOURCE ELIGIBLE.

RESOURCE ELIGIBLE != RESOURCE AUTHORIZED.

## CIM-05 — Ranking is deterministic

Eligible candidates SHALL be ranked deterministically.

Ranking SHALL prioritize:

1. evidence quality
2. reliability
3. privacy
4. lower cost
5. lower latency
6. stable resource identity

Equivalent input SHALL produce equivalent selection.

RANKED FIRST != SYSTEM TRUTH.

## CIM-06 — Unknown evidence fails closed

UNKNOWN availability SHALL NOT satisfy eligibility.

Missing eligible coverage for any required capability SHALL fail closed.

UNKNOWN != AVAILABLE.

NO ELIGIBLE RESOURCE != USE ANY RESOURCE.

## CIM-07 — Locality and privacy are first-class policy

Mission-bound resource policy SHALL explicitly represent locality
and privacy requirements.

A local-only mission SHALL reject remote and unknown-locality candidates.

PRIVACY PREFERENCE != PRIVACY GUARANTEE.

LOCAL RESOURCE != TRUSTED RESOURCE.

## CIM-08 — Selection grants no authority

Resource selection SHALL NOT grant:

- provider authority
- model authority
- runtime authority
- mission authority
- activation authorization
- execution authorization
- system truth

RESOURCE SELECTED != RESOURCE ACTIVATED.

RESOURCE SELECTED != EXECUTION AUTHORIZED.

MODEL SELECTED != MODEL AUTHORITY.

PROVIDER SELECTED != PROVIDER AUTHORITY.

## CIM-09 — Resources are replaceable without semantic drift

Two different resources capable of satisfying the same generic
capability contract MAY replace one another without changing:

- mission objective
- capability graph
- Council authority
- constitutional identity

MODEL SWITCH != MISSION CHANGE.

PROVIDER SWITCH != AUTHORITY CHANGE.

RUNTIME SWITCH != CORE MUTATION.

## CIM-10 — Existing market and sovereign router remain reusable

The existing Intelligence Market, scorecards, portfolios,
Council capability profiles and Sovereign Router remain valid
downstream/upstream evidence and operational mechanisms.

CIM0.1 does not replace them.

Existing law remains:

MAESTRO selects intelligence resources.

No model selects itself.

CIM0.1 performs no inference execution, network access,
provider invocation, model invocation, activation or mission execution.

## Canonical boundary

MISSION CAPABILITY DEMAND
        |
        v
GENERIC CAPABILITY GRAPH
        |
        v
RESOURCE CANDIDATES
        |
        +---- CAPABILITY
        +---- AVAILABILITY
        +---- EVIDENCE QUALITY
        +---- RELIABILITY
        +---- PRIVACY
        +---- COST
        +---- LATENCY
        +---- LOCALITY
        +---- OPAQUE PROVIDER/MODEL/RUNTIME METADATA
        |
        v
MISSION-BOUND POLICY
        |
        v
DETERMINISTIC ELIGIBILITY
        |
        v
DETERMINISTIC RANKING
        |
        v
RESOURCE SELECTION
        |
        v
BOUNDARY STOPS

## Constitutional separations

CAPABILITY != PROVIDER

CAPABILITY != MODEL

CAPABILITY != RUNTIME

TECHNOLOGY IDENTITY != MISSION SEMANTICS

RESOURCE AVAILABLE != RESOURCE ELIGIBLE

RESOURCE ELIGIBLE != RESOURCE AUTHORIZED

UNKNOWN != AVAILABLE

RESOURCE SELECTED != RESOURCE ACTIVATED

RESOURCE SELECTED != EXECUTION AUTHORIZED

MODEL SELECTED != MODEL AUTHORITY

PROVIDER SELECTED != PROVIDER AUTHORITY

MODEL SWITCH != MISSION CHANGE

PROVIDER SWITCH != AUTHORITY CHANGE

RUNTIME SWITCH != CORE MUTATION

## Final invariant

MAESTRO SHALL SELECT REPLACEABLE INTELLIGENCE RESOURCES THROUGH
GENERIC CAPABILITY CONTRACTS AND EXPLICIT MISSION-BOUND EVIDENCE
AND POLICY WHILE PROVIDER, MODEL AND RUNTIME IDENTITIES REMAIN
OPAQUE EDGE METADATA THAT NEVER ACQUIRE MISSION, COUNCIL,
ACTIVATION OR EXECUTION AUTHORITY.
