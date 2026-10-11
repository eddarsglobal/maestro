# MAESTRO Governed Mission Plan Constitution

## Scope

GMP0.1 governs:

- BM2-013 Plan Synthesis
- BM2-014 Plan Validation
- BM2-015 Effect Budget

It operates strictly before execution.

## GMP-01 — Plan lineage is explicit

Every mission plan SHALL bind:

- mission contract
- Council graph
- capability graph
- resource selection

Cross-lineage planning SHALL fail closed.

PLAN != MISSION AUTHORITY.

## GMP-02 — Every required capability becomes an explicit node

Every capability in the capability graph SHALL appear exactly once
in the governed mission plan.

Each node SHALL bind:

- capability
- owning Council
- selected resource
- dependencies
- acceptance evidence
- retry policy
- effects and permissions
- resource budgets
- sandbox requirement
- recovery boundary

NODE CREATED != NODE EXECUTED.

## GMP-03 — Dependencies form a DAG

Dependencies SHALL reference existing plan nodes.

Self-dependencies and cycles SHALL fail closed.

DAG VALID != DAG EXECUTED.

NODE READY != NODE EXECUTED.

## GMP-04 — Acceptance evidence is declared before execution

Each node SHALL declare evidence required to judge completion.

Mission acceptance criteria remain bound to the mission plan.

OUTPUT PRODUCED != ACCEPTANCE PROVEN.

EXECUTED != ACCEPTED.

## GMP-05 — Retry policy is explicit

Each node SHALL declare bounded retry behavior before execution.

Retry policy SHALL NOT itself trigger execution.

RETRY POSSIBLE != RETRY AUTHORIZED.

RETRY POLICY != RETRY EXECUTION.

## GMP-06 — Effects and permissions are explicit

Every node SHALL declare:

- effect classes
- permissions
- tool-call budget
- cost budget
- latency budget
- network allowance
- filesystem-write allowance
- sandbox requirement

EFFECT DECLARED != EFFECT AUTHORIZED.

PERMISSION DECLARED != PERMISSION GRANTED.

## GMP-07 — External effects require an explicit sandbox boundary

Network or filesystem-write effects SHALL require matching permission
declarations and an explicit sandbox requirement.

SANDBOX REQUIRED != SANDBOX EXECUTED.

NETWORK DECLARED != NETWORK AUTHORIZED.

FILESYSTEM WRITE DECLARED != FILESYSTEM WRITE AUTHORIZED.

## GMP-08 — AY and relevant Councils validate before eligibility

Execution eligibility SHALL require explicit PASS evidence from:

- AY
- plan-invariant validation
- every relevant node-owning Council
- all mission acceptance criteria

Missing or UNKNOWN validation evidence SHALL remain UNKNOWN.

Any explicit FAIL SHALL reject the plan.

VALIDATED != EXECUTION AUTHORIZED.

## GMP-09 — Eligibility grants no execution or effect authority

GMP0.1 MAY determine EXECUTION_ELIGIBLE.

It SHALL NOT assert:

- execution authorization
- effect authorization
- network authorization
- filesystem-write authorization
- system truth

EXECUTION_ELIGIBLE != EXECUTION_AUTHORIZED.

PLAN VALIDATED != EFFECT AUTHORIZED.

## GMP-10 — Existing runtime remains downstream

Existing DagEngine, Dispatcher, RetryLedger, Sandbox and EffectJournal
remain downstream execution mechanisms.

GMP0.1 SHALL NOT invoke them.

Only existing downstream constitutional authority may start nodes,
perform effects, retry work or mutate mission state.

PLAN SYNTHESIS != RUNTIME EXECUTION.

## Canonical boundary

MISSION CONTRACT
    +
COUNCIL GRAPH
    +
CAPABILITY GRAPH
    +
RESOURCE SELECTION
    |
    v
CAPABILITY PLAN DIRECTIVES
    |
    v
GOVERNED MISSION DAG
    |
    +---- COUNCIL OWNER
    +---- RESOURCE
    +---- DEPENDENCIES
    +---- ACCEPTANCE EVIDENCE
    +---- RETRY POLICY
    +---- EFFECTS
    +---- PERMISSIONS
    +---- BUDGETS
    +---- SANDBOX
    +---- RECOVERY BOUNDARY
    |
    v
AY + COUNCIL + INVARIANT + ACCEPTANCE VALIDATION
    |
    +---- REJECTED
    +---- UNKNOWN
    +---- EXECUTION_ELIGIBLE
    |
    v
BOUNDARY STOPS

## Constitutional separations

PLAN CREATED != PLAN AUTHORIZED

NODE CREATED != NODE EXECUTED

DAG VALID != DAG EXECUTED

NODE READY != NODE EXECUTED

OUTPUT PRODUCED != ACCEPTANCE PROVEN

RETRY POSSIBLE != RETRY AUTHORIZED

RETRY POLICY != RETRY EXECUTION

EFFECT DECLARED != EFFECT AUTHORIZED

PERMISSION DECLARED != PERMISSION GRANTED

SANDBOX REQUIRED != SANDBOX EXECUTED

NETWORK DECLARED != NETWORK AUTHORIZED

FILESYSTEM WRITE DECLARED != FILESYSTEM WRITE AUTHORIZED

VALIDATED != EXECUTION AUTHORIZED

EXECUTION_ELIGIBLE != EXECUTION_AUTHORIZED

PLAN VALIDATED != EFFECT AUTHORIZED

PLAN SYNTHESIS != RUNTIME EXECUTION

## Final invariant

MAESTRO SHALL BUILD A DETERMINISTIC MISSION DAG WITH EXPLICIT
COUNCIL OWNERSHIP, RESOURCE BINDING, DEPENDENCIES, ACCEPTANCE
EVIDENCE, RETRY, EFFECT, PERMISSION, BUDGET, SANDBOX AND RECOVERY
BOUNDARIES, AND MAY DECLARE THAT PLAN EXECUTION-ELIGIBLE ONLY
AFTER EXPLICIT AY AND RELEVANT-COUNCIL VALIDATION, WITHOUT
GMP0.1 ITSELF AUTHORIZING OR EXECUTING ANY EFFECT OR NODE.
