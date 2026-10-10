# MAESTRO Orchestration Cost Avoidance Constitution

> Governing contract for selecting the least orchestration sufficient for a unit of work.

## Status

This constitution formalizes BordingMap point `BMF-014`.

It governs path selection across Atomic, Cognitive and Fabric work without granting execution authority.

## OCA-01 — Least orchestration sufficient

MAESTRO SHALL select the least orchestration path sufficient for the declared work requirements.

Additional Councils, intelligence resources, cognitive depth, Fabric distribution, remote capacity, cross-node state, or other orchestration SHALL NOT be introduced merely because those facilities are available.

## OCA-02 — Atomic path is the zero-orchestration baseline

When work requires no cognition and no Fabric property, MAESTRO SHALL select `ATOMIC`.

An Atomic decision SHALL require zero Councils, zero intelligence-resource calls, zero cognitive depth, and zero Fabric requirement.

Atomic path selection SHALL NOT activate Councils, invoke intelligence resources, dispatch Fabric work, or use the network.

## OCA-03 — Cognitive path is demand-driven

When cognition is required and Fabric is not required, MAESTRO SHALL select `COGNITIVE`.

Cognition may be required explicitly or by declared Council requirements, resource-call requirements, or cognitive-depth requirements.

The decision SHALL preserve exactly the declared Council set, resource-call count, and cognitive depth. It SHALL NOT silently fan out to extra Councils or increase cognitive work.

## OCA-04 — Fabric path requires a Fabric reason

MAESTRO SHALL select `FABRIC` only when the declared work requires distribution, remote capacity, or cross-node state.

Cognitive need alone SHALL NOT force Fabric selection.

Fabric selection SHALL NOT itself dispatch work or establish remote execution authority.

## OCA-05 — Orchestration cost ordering is explicit

The canonical path-cost ordering is:

```text
ATOMIC    = 0
COGNITIVE = 1
FABRIC    = 2
```

The ranking expresses orchestration burden only. It is not a quality verdict, authority ranking, trust ranking, or system-truth ranking.

## OCA-06 — Council participation is on-demand

Path selection SHALL preserve the exact declared Council set in deterministic order.

No Council SHALL be added simply because it exists in the Genesis registry or is currently resident.

Selection SHALL NOT activate a Council. Existing Council lifecycle mechanisms remain responsible for governed residency and activation at their own boundary.

## OCA-07 — Cognitive and orchestration ceilings fail closed

Policy MAY prohibit Cognitive or Fabric paths and MAY impose maximum Council count, maximum resource calls, and maximum cognitive depth.

If required work exceeds an active ceiling, selection SHALL fail closed rather than silently reducing requirements or exceeding the policy.

## OCA-08 — Decisions are deterministic and requirement-preserving

Equivalent work requirements and policies SHALL produce equivalent path decisions independent of unordered input representation.

The selector SHALL NOT add, remove, or rewrite declared Council, resource-call, cognitive-depth, cognition, or Fabric requirements.

## OCA-09 — Performance grants no authority

```text
PATH SELECTED
    !=
COUNCIL ACTIVATED
    !=
INTELLIGENCE EXECUTED
    !=
FABRIC DISPATCHED
    !=
NETWORK AUTHORIZED
    !=
SYSTEM TRUTH
```

A performance decision SHALL be selection-only and SHALL grant no AY verdict, EX authorization, activation authority, intelligence-execution authority, Fabric-dispatch authority, network authority, promotion authority, or system truth.

## OCA-10 — Selector remains passive

The orchestration-cost selector SHALL perform no Council runtime import, intelligence-market invocation, provider invocation, Fabric runtime invocation, network access, process execution, activation, dispatch, installation, execution, learning, or promotion.

Invalid types, invalid budgets, forbidden paths, exceeded ceilings, unnecessary path escalation, and authority escalation SHALL fail closed.

## Canonical decision ladder

```text
NO COGNITION + NO FABRIC REQUIREMENT
    -> ATOMIC

COGNITION REQUIRED + NO FABRIC REQUIREMENT
    -> COGNITIVE

DISTRIBUTION OR REMOTE CAPACITY OR CROSS-NODE STATE REQUIRED
    -> FABRIC
```

## Relationship to existing subsystems

`CognitiveEconomy` continues to govern cognitive budgets and adaptive depth.

`MinimumSufficientResourceSelector` continues to govern minimum-sufficient intelligence and compute resources.

`CouncilLifecycleManager` continues to govern Council residency and activation.

Fabric placement and execution remain separate downstream boundaries.

OCA0.1 does not replace or silently integrate those systems. It establishes the passive path-selection contract that precedes them.

## BordingMap boundary

```text
BMF-013 = minimum sufficient governed intelligence and compute resources
BMF-014 = Atomic, Cognitive and Fabric paths avoid unnecessary orchestration cost
BMF-015 = platform-specific discovery and execution remain behind generic governed contracts
```

BMF-014 certifies path selection and orchestration-cost avoidance only.

It does not certify automatic runtime execution, Council activation, model invocation, Fabric dispatch, remote execution, or network use.

## Required objects

```text
OrchestrationPath
WorkRequirements
OrchestrationCostPolicy
OrchestrationPathDecision
GovernedOrchestrationPathSelector
```

## Evidence requirements

A checkpoint claiming BMF-014 conformance SHALL demonstrate at least:

1. Atomic, Cognitive and Fabric paths are explicit;
2. Atomic work selects Atomic;
3. Atomic work requires zero Councils;
4. Atomic work requires zero intelligence-resource calls;
5. Atomic work requires zero cognitive depth;
6. Atomic work requires zero Fabric;
7. Cognitive work selects Cognitive without Fabric when Fabric is not required;
8. Cognitive decisions preserve the exact declared Council set;
9. Cognitive decisions preserve exact resource-call and cognitive-depth requirements;
10. distribution selects Fabric;
11. remote-capacity need selects Fabric;
12. cross-node-state need selects Fabric;
13. unnecessary path escalation fails closed;
14. policy ceilings fail closed;
15. decisions are deterministic;
16. no Council activation occurs during selection;
17. no intelligence execution occurs during selection;
18. no Fabric dispatch occurs during selection;
19. no network access occurs during selection;
20. selection grants no downstream authority or system truth;
21. BordingMap point `BMF-014` is explicitly assessed with evidence.

## Final invariant

> MAESTRO SHALL USE THE LEAST ORCHESTRATION SUFFICIENT FOR THE WORK.

> PATH SELECTION != EXECUTION. PERFORMANCE != AUTHORITY.
