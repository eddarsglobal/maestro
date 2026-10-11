# BM2 Adaptive Mission Closure Certification

Checkpoint: AMC0.1

## BM2-019 — Adaptive Routing — PASS

Certified properties:

- route failure evidence is explicit
- route failure evidence binds routing-plan identity
- route failure evidence binds node identity
- route failure evidence binds capability identity
- route failure evidence binds current resource
- UNKNOWN failure remains UNKNOWN
- explicit absence of failure produces NO_CHANGE
- detected failure triggers governed replacement evaluation
- failed resource cannot replace itself
- replacement uses existing mission-bound resource policy
- replacement uses generic capability contract
- no eligible replacement produces REPLAN_REQUIRED
- mission objective is preserved
- Council ownership is preserved
- provider/model/resource authority is not granted
- reroute proposal does not execute
- replan requirement does not execute replan
- no mission-state transition is requested

## BM2-020 — Evidence Closure — PASS

Certified properties:

- node closure binds exact mission plan
- node closure binds exact routing plan
- node closure binds exact route
- node closure binds exact idempotency key
- execution state is explicit
- output reference is explicit
- provenance evidence is required
- execution evidence is required
- relevant Council verdict is required
- Council verdict reference is required
- node acceptance evidence is required
- execution success alone is insufficient
- incomplete evidence yields UNKNOWN
- explicit execution failure yields REJECTED
- explicit Council-verdict failure yields REJECTED
- complete evidence yields COMPLETE
- node closure grants no mission-close authority
- node closure grants no learning authority

## BM2-021 — Mission Verdict — PASS

Certified properties:

- mission verdict binds exact mission plan
- all planned node closures are required
- every node closure must be COMPLETE
- all mission acceptance criteria are required
- all relevant Council verdicts are required
- relevant Council verdicts must PASS
- Council verdict references are required
- AY SYSTEM verdict evidence is required
- AY SYSTEM verdict must PASS
- AY SYSTEM verdict reference is required
- explicit failure produces REJECTED
- incomplete evidence produces UNKNOWN
- complete evidence produces ACCEPTED
- execution completion alone does not imply acceptance
- evidence completeness is distinct from mission acceptance
- ACCEPTED does not assert system truth
- ACCEPTED does not authorize Kernel.close
- ACCEPTED does not request canonical state transition
- ACCEPTED does not authorize durable commit
- ACCEPTED does not authorize learning
- ACCEPTED does not authorize promotion
- existing EX/AY/TX constitutional closure remains downstream

## BordingMap 2.0 state

TOTAL: 32

PASS: 21

DEFERRED: 11

BLOCKED: 0

MISSING: 0

NEXT: BM2-022

PROJECT_COMPLETE: FALSE

## Constitutional separations

FAILURE SUSPECTED != FAILURE PROVEN

UNKNOWN FAILURE != FAILURE ABSENT

REROUTE != OBJECTIVE CHANGE

RESOURCE CHANGE != MISSION CHANGE

RESOURCE CHANGE != COUNCIL CHANGE

REPLACEMENT AVAILABLE != REPLACEMENT AUTHORIZED

REPLAN REQUIRED != REPLAN EXECUTED

REROUTE PROPOSED != REROUTE EXECUTED

ADAPTIVE ROUTING != EXECUTION AUTHORITY

EXECUTION SUCCESS != EVIDENCE COMPLETE

OUTPUT != PROVENANCE

MISSING EVIDENCE != PASS

UNKNOWN != ACCEPTED

DAG COMPLETE != MISSION ACCEPTED

NODE COMPLETE != MISSION ACCEPTED

EXECUTION COMPLETE != EVIDENCE COMPLETE

EVIDENCE COMPLETE != MISSION ACCEPTED

MISSION ACCEPTED != SYSTEM TRUTH

MISSION VERDICT != MISSION CLOSE AUTHORITY

ACCEPTED != TASK_COMPLETE

VERDICT ARTIFACT != CAN_CLOSE

CAN_CLOSE != STATE TRANSITION
