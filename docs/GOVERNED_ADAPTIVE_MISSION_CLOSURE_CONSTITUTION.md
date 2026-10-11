# MAESTRO Governed Adaptive Mission Closure Constitution

## Scope

AMC0.1 governs:

- BM2-019 Adaptive Routing
- BM2-020 Evidence Closure
- BM2-021 Mission Verdict

AMC0.1 remains passive.

It does not execute reroutes, mutate a DAG, transition mission state,
close missions, authorize durable commits or authorize learning.

## AMC-01 — Failure evidence is explicit

Adaptive routing SHALL begin only from explicit route-bound failure evidence.

Failure evidence SHALL bind:

- routing plan
- route
- node
- capability
- current resource
- failure kind

FAILURE SUSPECTED != FAILURE PROVEN.

UNKNOWN FAILURE != FAILURE ABSENT.

## AMC-02 — Rerouting preserves mission semantics

A resource failure MAY produce a replacement-resource proposal.

The proposal SHALL preserve:

- mission-contract identity
- mission objective
- capability identity
- owning Council
- constitutional authority

REROUTE != OBJECTIVE CHANGE.

RESOURCE CHANGE != MISSION CHANGE.

RESOURCE CHANGE != COUNCIL CHANGE.

## AMC-03 — Rerouting reuses governed resource eligibility

Replacement resources SHALL satisfy the existing generic capability
and mission-bound selection policy.

The failed resource SHALL NOT be selected as its own replacement.

No eligible replacement SHALL produce REPLAN_REQUIRED.

REPLACEMENT AVAILABLE != REPLACEMENT AUTHORIZED.

REPLAN REQUIRED != REPLAN EXECUTED.

## AMC-04 — Adaptive routing grants no execution authority

A reroute proposal SHALL NOT:

- execute the replacement
- mutate the current route
- mutate the mission DAG
- grant provider authority
- grant model authority
- grant resource authority
- transition mission state

REROUTE PROPOSED != REROUTE EXECUTED.

ADAPTIVE ROUTING != EXECUTION AUTHORITY.

## AMC-05 — Node closure requires complete evidence

A node SHALL NOT be evidence-complete merely because execution reports success.

Complete node closure requires:

- exact plan/route lineage
- exact idempotency key
- execution PASS
- output reference
- provenance references
- execution evidence references
- owning-Council verdict PASS
- owning-Council verdict reference
- complete node acceptance evidence

EXECUTION SUCCESS != EVIDENCE COMPLETE.

OUTPUT != PROVENANCE.

## AMC-06 — Missing evidence remains UNKNOWN

Missing or UNKNOWN execution, provenance, verdict or acceptance evidence
SHALL keep node closure UNKNOWN.

Explicit execution or Council-verdict failure SHALL produce REJECTED.

MISSING EVIDENCE != PASS.

UNKNOWN != ACCEPTED.

## AMC-07 — Mission verdict requires complete node closure

Mission acceptance requires every planned node to have a COMPLETE governed
node closure.

One successful node or an execution-complete DAG is insufficient.

DAG COMPLETE != MISSION ACCEPTED.

NODE COMPLETE != MISSION ACCEPTED.

## AMC-08 — Mission verdict requires governed acceptance evidence

Mission ACCEPTED requires:

- every node closure COMPLETE
- every mission acceptance criterion validated
- every relevant Council verdict PASS
- verdict references present
- AY SYSTEM verdict PASS
- AY SYSTEM verdict reference present

EXECUTION COMPLETE != EVIDENCE COMPLETE.

EVIDENCE COMPLETE != MISSION ACCEPTED.

MISSION ACCEPTED != SYSTEM TRUTH.

## AMC-09 — Verdict is not lifecycle authority

AMC0.1 may determine ACCEPTED, REJECTED or UNKNOWN.

AMC0.1 SHALL NOT:

- call Kernel.close
- transition canonical mission state
- authorize durable commit
- authorize learning
- authorize promotion
- assert system truth

MISSION VERDICT != MISSION CLOSE AUTHORITY.

ACCEPTED != TASK_COMPLETE.

## AMC-10 — Existing constitutional closure remains downstream

Existing constitutional mechanisms remain authoritative downstream:

- EX owns canonical mission-state transitions
- AY owns SYSTEM verdict validation
- constitution.can_close owns closure eligibility
- TX owns governed durable commit
- Kernel.close performs canonical mission closure
- Outcome Intelligence accepts only AY-verified outcomes

AMC0.1 supplies bounded evidence and verdict artifacts only.

VERDICT ARTIFACT != CAN_CLOSE.

CAN_CLOSE != STATE TRANSITION.

## Canonical boundary

EXECUTION / RESOURCE FAILURE
        |
        v
ROUTE-BOUND FAILURE EVIDENCE
        |
        +---- FAILURE UNKNOWN
        |          |
        |          v
        |       UNKNOWN
        |
        +---- NO FAILURE
        |          |
        |          v
        |       NO_CHANGE
        |
        +---- FAILURE PASS
                   |
                   v
         GOVERNED RESOURCE RE-SELECTION
                   |
            +------+------+
            |             |
            v             v
       REPLACEMENT     NO REPLACEMENT
            |             |
            v             v
    REROUTE_PROPOSED  REPLAN_REQUIRED
            |
            v
       BOUNDARY STOPS

EXECUTION RESULT
        |
        v
OUTPUT + PROVENANCE + EXECUTION EVIDENCE
        |
        +
COUNCIL VERDICT
        |
        +
NODE ACCEPTANCE EVIDENCE
        |
        v
NODE CLOSURE
        |
        +---- COMPLETE
        +---- REJECTED
        +---- UNKNOWN
        |
        v
ALL NODE CLOSURES
        |
        +
MISSION ACCEPTANCE CRITERIA
        |
        +
DOMAIN COUNCIL VERDICTS
        |
        +
AY SYSTEM VERDICT
        |
        v
MISSION VERDICT
        |
        +---- ACCEPTED
        +---- REJECTED
        +---- UNKNOWN
        |
        v
BOUNDARY STOPS
        |
        v
EXISTING CONSTITUTIONAL MISSION CLOSURE

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

## Final invariant

MAESTRO MAY RESPOND TO RESOURCE FAILURE BY PROPOSING A GOVERNED
RESOURCE REROUTE OR REPLAN WHILE PRESERVING THE MISSION OBJECTIVE,
AND MAY DERIVE NODE CLOSURE AND A MISSION VERDICT ONLY FROM COMPLETE
OUTPUT, PROVENANCE, EXECUTION, ACCEPTANCE AND COUNCIL/AY VERDICT
EVIDENCE, WITHOUT AMC0.1 ITSELF EXECUTING, CLOSING, LEARNING FROM
OR CHANGING THE CANONICAL MISSION.
