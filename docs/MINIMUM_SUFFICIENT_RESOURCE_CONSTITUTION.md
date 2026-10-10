# MAESTRO Minimum Sufficient Resource Constitution

> Governing contract for selecting the minimum sufficient intelligence or compute resource for a mission.

## Status

This constitution formalizes BordingMap point `BMF-013`.

It builds on generic resource descriptors, replaceable adapter registration, sovereign degraded operation, and the existing Cognitive Economy.

## MSR-01 — Sufficiency precedes optimization

MAESTRO SHALL determine whether a resource satisfies the governed mission envelope before comparing that resource economically with other candidates.

An under-capable resource SHALL NOT become eligible merely because it is cheaper, faster, smaller, local, familiar, or historically successful.

## MSR-02 — Capability requirements are explicit

The mission SHALL provide an explicit non-empty set of required capability identifiers.

A resource is capability-sufficient only when its generic capability set contains every required capability.

Unknown future capability identifiers SHALL remain admissible.

## MSR-03 — Governed sufficiency envelope

Capability sufficiency alone is not enough.

The policy MAY additionally establish a minimum quality floor, maximum cost ceiling, maximum latency ceiling, maximum governed resource-mass ceiling, and explicit forbidden-resource set.

A candidate outside any active boundary SHALL be rejected before optimization.

## MSR-04 — Excess capability is over-provisioning

For resources that already satisfy the mission envelope, capabilities beyond the required capability set SHALL be treated as excess capability mass.

MAESTRO SHALL prefer fewer excess capabilities before preferring economic advantages that would otherwise reward unnecessary over-provisioning.

Over-provisioned resources are not absolutely forbidden; they MAY be selected when smaller resources fail the governed sufficiency envelope.

## MSR-05 — Governed resource mass is minimized

After excess capability mass, MAESTRO SHALL prefer the lower governed resource-mass score.

Resource mass is generic economic input and SHALL NOT be constitutionally defined by any contemporary model size, hardware family, provider, runtime, accelerator, protocol, or vendor.

## MSR-06 — Economic ranking follows sufficiency

Among candidates with equivalent excess capability mass and governed resource mass, MAESTRO SHALL prefer lower cost, then lower latency, then higher quality.

Quality SHALL never compensate for failure of a required capability or another hard sufficiency boundary.

## MSR-07 — Selection is deterministic

Equivalent resource sets, economy profiles, and policies SHALL produce equivalent decisions independent of input ordering.

When all governed ranking dimensions are equal, resource identity SHALL provide the deterministic final tie-break.

## MSR-08 — Intelligence and compute share the generic contract

Minimum-sufficient selection SHALL operate on `GenericResourceDescriptor` and SHALL NOT require provider identity, model identity, runtime identity, hardware family, or any technology identity specific to one era.

The same selection contract SHALL therefore be usable for intelligence resources, compute resources, and future resource technologies not known when this constitution was written.

## MSR-09 — Economy grants no authority

```text
ECONOMICALLY SELECTED
    !=
TRUSTED
    !=
INSTALLED
    !=
ACTIVATED
    !=
AUTHORIZED
    !=
EXECUTED
    !=
SYSTEM TRUTH
```

A minimum-sufficient decision SHALL be selection-only.

It SHALL grant no AY verdict, EX authorization, trust, installation authority, activation authority, execution authority, promotion authority, or system truth.

## MSR-10 — Selection remains passive and fail-closed

Minimum-sufficient selection SHALL perform no network access, external process execution, installation, activation, resource execution, provider invocation, learning, promotion, or authority escalation.

Duplicate resource identities, duplicate economy profiles, missing economy profiles, resource/profile identity inconsistencies, invalid policy scores, and absence of any sufficient candidate SHALL fail closed.

## Canonical ranking order

After all hard sufficiency constraints have passed, candidates SHALL be ranked by:

```text
1. least excess capability count
2. least governed resource mass
3. least cost
4. least latency
5. highest quality
6. deterministic resource_id
```

This order prevents a substantially over-provisioned resource from winning merely because it has superior quality, cost, or latency scores.

## BordingMap boundary

```text
BMF-008 = resource selection remains capability-first — Evergreen
BMF-012 = discovery remains distinct from trust/install/activate/authorize/execute — Evergreen
BMF-013 = MAESTRO selects minimum sufficient governed intelligence and compute resources
```

BMF-013 certifies a selection contract.

It does not certify execution, activation, installation, trust, authorization, resource availability probing, procurement, or automatic use of the selected resource.

## Required objects

```text
GovernedResourceEconomyProfile
MinimumSufficientResourcePolicy
MinimumSufficientResourceCandidate
MinimumSufficientResourceDecision
MinimumSufficientResourceSelector
```

## Evidence requirements

A checkpoint claiming BMF-013 conformance SHALL demonstrate at least:

1. required capabilities are evaluated before optimization;
2. under-capable resources are rejected;
3. the quality floor is enforced;
4. the cost ceiling is enforced;
5. the latency ceiling is enforced;
6. the governed resource-mass ceiling is enforced;
7. a sufficient smaller-capability resource defeats unjustified over-provisioning;
8. lower governed resource mass wins when capability excess is equal;
9. deterministic tie-breaking is independent of input order;
10. generic intelligence resources are supported;
11. generic compute resources are supported;
12. unknown future resource kinds and capability identifiers are supported;
13. provider and model identities are not required;
14. resource/economy-profile integrity fails closed;
15. selection grants no trust, activation, execution, authorization, or system truth;
16. selector operation requires no network or external process;
17. BordingMap point `BMF-013` is explicitly assessed with evidence.

## Final invariant

> MAESTRO SHALL SPEND NO MORE INTELLIGENCE OR COMPUTE CAPABILITY THAN IS GOVERNEDLY SUFFICIENT FOR THE MISSION.

Minimum sufficient does not mean weakest regardless of fitness.

It means the least governed resource envelope that first satisfies the mission constraints.
