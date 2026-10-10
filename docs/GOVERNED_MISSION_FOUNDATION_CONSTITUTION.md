# MAESTRO Governed Mission Foundation Constitution

## Scope

MCF0.1 governs:

- BM2-005 mission-contract
- BM2-006 mission-analysis
- BM2-007 council-synthesis

It creates no execution authority.

It selects no model, provider, runtime or tool.

It activates no Council.

## MCF-01 — Mission contract is explicit

User intent SHALL be represented by an explicit mission contract.

The contract SHALL contain:

- objective
- scope
- requested output
- constraints
- acceptance criteria
- authority requirements
- evidence obligations

MISSION CREATED != MISSION AUTHORIZED.

OBJECTIVE != METHOD.

REQUESTED OUTPUT != ACCEPTANCE PROOF.

## MCF-02 — Contract identity is deterministic

Equivalent semantic mission-contract content SHALL produce equivalent contract identity.

Ordering of set-like constraints, criteria, authority requirements and evidence obligations SHALL NOT alter identity.

CONTRACT IDENTITY != SYSTEM TRUTH.

## MCF-03 — Mission analysis derives capabilities, not technologies

Mission analysis SHALL derive generic capability demand.

It SHALL NOT select:

- provider
- model
- runtime
- tool
- hardware
- execution adapter

CAPABILITY != PROVIDER.

CAPABILITY DEMAND != RESOURCE SELECTION.

ANALYSIS != EXECUTION.

## MCF-04 — Analysis is explicit and fail-closed

Capability derivation SHALL use explicit deterministic rules.

Missing derivation evidence SHALL NOT fabricate a capability.

A mission for which no capability demand can be derived SHALL fail closed.

UNKNOWN CAPABILITY != KNOWN CAPABILITY.

NO MATCH != NO CAPABILITY REQUIRED.

## MCF-05 — Capability demand is contract-bound

Every capability-demand result SHALL bind the exact mission-contract identity.

A demand SHALL NOT be silently rebound to another mission contract.

MISSION CONTRACT != CAPABILITY DEMAND.

DEMAND REBINDING SHALL FAIL CLOSED.

## MCF-06 — Council synthesis uses capability coverage

Council synthesis SHALL consume generic capability demand and explicit Council capability bindings.

Council choice SHALL be based on required capability coverage rather than provider/model identity.

COUNCIL != MODEL.

COUNCIL != PROVIDER.

COUNCIL REQUIRED != COUNCIL ACTIVATED.

## MCF-07 — Council graph is minimal

Among existing Councils capable of fully covering a mission demand, MCF0.1 SHALL select a minimum-cardinality capability-covering set.

Equivalent minimum solutions SHALL use deterministic lexical tie-breaking.

EX routing authority and AY acceptance authority SHALL remain explicitly present.

MINIMAL GRAPH != MINIMAL AUTHORITY.

## MCF-08 — Missing Council coverage fails closed

If existing Council bindings cannot cover all demanded capabilities, graph synthesis SHALL fail closed.

MCF0.1 SHALL NOT:

- fabricate a Council
- install a Council
- propose a dynamic Council
- activate a Council

Council-gap evidence and dynamic Council proposals belong to BM2-008 and BM2-009.

MISSING COUNCIL CAPABILITY != DYNAMIC COUNCIL AUTHORIZED.

## MCF-09 — Graph construction grants no execution authority

Mission analysis and Council graph synthesis SHALL NOT assert:

- resource selection
- provider selection
- model selection
- Council activation
- execution request
- execution authorization
- system truth

PLAN FOUNDATION != EXECUTION AUTHORIZATION.

GRAPH READY != NODE EXECUTED.

## MCF-10 — Existing runtime authority remains downstream

MCF0.1 SHALL NOT replace the existing mission runtime, DAG engine, dispatcher or EX/AY authority model.

The existing runtime MAY consume mission-contract, capability-demand and Council-graph artifacts through explicit future integration bridges.

MCF0.1 performs no network access, model invocation, tool invocation, persistence mutation, Council activation or mission-state transition.

MISSION FOUNDATION != MISSION EXECUTION.

## Canonical boundary

USER INTENT
    |
    v
MISSION CONTRACT
    |
    v
DETERMINISTIC CAPABILITY RULES
    |
    v
GENERIC CAPABILITY DEMAND
    |
    v
EXPLICIT COUNCIL-CAPABILITY BINDINGS
    |
    v
MINIMAL COUNCIL GRAPH
    |
    +---- EX ROUTING AUTHORITY
    |
    +---- AY ACCEPTANCE AUTHORITY
    |
    +---- MINIMUM CAPABILITY WORKERS
    |
    v
BOUNDARY STOPS

The boundary stops before:

- resource selection
- provider selection
- model selection
- tool selection
- Council activation
- DAG execution
- mission-state transition
- system-truth assertion

## Constitutional separations

MISSION CREATED != MISSION AUTHORIZED

MISSION CONTRACT != CAPABILITY DEMAND

CAPABILITY != PROVIDER

CAPABILITY DEMAND != RESOURCE SELECTION

COUNCIL != MODEL

COUNCIL REQUIRED != COUNCIL ACTIVATED

MISSING COUNCIL CAPABILITY != DYNAMIC COUNCIL AUTHORIZED

PLAN FOUNDATION != EXECUTION AUTHORIZATION

GRAPH READY != NODE EXECUTED

MISSION FOUNDATION != MISSION EXECUTION

## Final invariant

MAESTRO MAY TRANSFORM EXPLICIT USER INTENT INTO A DETERMINISTIC MISSION CONTRACT, GENERIC CAPABILITY DEMAND AND MINIMAL EXISTING-COUNCIL GRAPH WITHOUT SELECTING TECHNOLOGY RESOURCES, ACTIVATING COUNCILS OR ACQUIRING EXECUTION AUTHORITY.
