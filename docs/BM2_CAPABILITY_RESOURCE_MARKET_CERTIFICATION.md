# BM2 Capability Resource Market Certification

Checkpoint: CIM0.1

## BM2-010 — Capability Graph — PASS

Certified properties:

- mission capability demand maps to generic capability contracts
- capability graph binds mission-contract identity
- capability graph binds capability-demand identity
- capability graph contains no provider binding
- capability graph contains no model binding
- capability graph contains no runtime binding
- graph identity is deterministic
- graph grants no resource selection authority
- graph grants no execution authority

## BM2-011 — Intelligence Market — PASS

Certified properties:

- resource candidates expose capability coverage
- availability evidence is explicit
- evidence quality is explicit
- reliability is explicit
- privacy score is explicit
- cost is explicit
- latency is explicit
- locality is explicit
- mission constraint references are explicit
- selection policy binds exact mission contract
- UNKNOWN availability fails closed
- failed availability fails closed
- locality requirements fail closed
- privacy requirements fail closed
- cost ceilings fail closed
- latency ceilings fail closed
- deterministic resource ranking
- deterministic tie-breaking
- missing eligible capability coverage fails closed
- existing Intelligence Market regressions remain green

## BM2-012 — Model Sovereignty — PASS

Certified properties:

- provider/model/runtime references are opaque candidate metadata
- provider identity is absent from capability graph identity
- model identity is absent from capability graph identity
- runtime identity is absent from capability graph identity
- resource replacement preserves capability semantics
- provider replacement preserves mission semantics
- model replacement preserves mission semantics
- runtime replacement preserves Core semantics
- no provider authority is granted
- no model authority is granted
- no runtime authority is granted
- no mission authority is transferred
- resource selection does not authorize activation
- resource selection does not authorize execution
- Sovereign Router law remains intact
- MAESTRO selects resources; models do not select themselves

## BordingMap 2.0 state

TOTAL: 32

PASS: 12

DEFERRED: 20

BLOCKED: 0

MISSING: 0

NEXT: BM2-013

PROJECT_COMPLETE: FALSE

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
