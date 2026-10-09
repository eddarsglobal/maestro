# MAESTRO Unknown Technology Research Ingress Constitution

> Governing contract for admitting unknown technologies into the passive RX and ADEL research path.

## Status

This constitution formalizes BordingMap point `BMF-011`.

It builds on generic discovery descriptors certified by `checkpoint-gdr0.1` and generic replaceable adapter registration certified by `checkpoint-gar0.1`.

## UTR-01 — Unknown technology may enter research

An unknown host, resource, or capability described through the generic discovery contracts SHALL be representable as research input without first becoming a known provider, model, runtime, protocol, or hardware family.

Research ingress SHALL preserve technological-time sovereignty.

## UTR-02 — Ingress is capability-first

Unknown-technology research candidacy SHALL be expressed around the capability that requires understanding.

Provider or model identity SHALL NOT be required for research ingress.

## UTR-03 — RX and ADEL are the governed ingress path

The passive ingress path SHALL remain explicitly `RX -> ADEL`.

Ingress establishes research candidacy only. It does not assert execution, installation, activation, trust, authorization, promotion, or truth.

## UTR-04 — Candidate is not ResearchRequest

An `UnknownTechnologyResearchCandidate` SHALL NOT be a `ResearchRequest`.

Ingress SHALL NOT materialize a `ResearchRequest`.

Any later request drafting, admission, materialization, routing, execution, review, or reevaluation SHALL cross its own already-governed boundary.

## UTR-05 — Research intent is passive SEARCH

Unknown-technology ingress candidates SHALL use the passive RX `SEARCH` research capability.

Ingress SHALL NOT silently escalate to FETCH, provider routing, tool execution, network access, or runtime execution.

## UTR-06 — Descriptor evidence is preserved

Host, resource, and capability descriptors supplied by generic discovery SHALL remain attached to the ingress candidate.

Their attributes and evidence references SHALL not be silently discarded or rewritten by ingress.

Preserved descriptor evidence is context, not verified system truth.

## UTR-07 — Candidate identity is deterministic

Equivalent generic discovery projections SHALL produce equivalent ingress candidates and deterministic candidate identifiers.

Candidate ordering SHALL be deterministic and capability-first.

## UTR-08 — Referential integrity fails closed

A resource SHALL remain bound to the projection host.

A capability SHALL be declared by both the host and the resource before an ingress candidate may represent that resource-capability pair.

Identity or capability inconsistencies SHALL fail closed.

## UTR-09 — Ingress grants no authority

```text
RESEARCH CANDIDATE
    !=
RESEARCH REQUEST
    !=
NETWORK ACCESS
    !=
TRUST
    !=
INSTALLATION
    !=
ACTIVATION
    !=
AUTHORIZATION
    !=
EXECUTION
    !=
SYSTEM TRUTH
```

Research candidacy SHALL grant no AY verdict, EX authorization, provider selection, installation authority, activation authority, execution authority, promotion authority, or system truth.

## UTR-10 — Existing RX and ADEL governance remains sovereign

This ingress SHALL reuse the existing RX and ADEL research architecture rather than bypass it.

Technology Radar, follow-up candidacy, request drafting, request materialization, routing, exact execution, evidence reintegration, review, and reevaluation remain separate governed stages.

Ingress SHALL NOT collapse those stages into one action.

## BordingMap boundary

```text
BMF-007 = generic host, capability, and resource discovery descriptors
BMF-010 = replaceable dynamic adapter registration
BMF-011 = unknown technologies can enter a governed RX and ADEL research path
```

BMF-011 certifies the research ingress boundary only.

It does not certify automatic network research, request materialization, provider selection, routing, execution, installation, activation, trust, authorization, or truth.

## Required objects

```text
UnknownTechnologyResearchCandidate
UnknownTechnologyResearchIngressResult
GovernedUnknownTechnologyResearchIngress
```

## Evidence requirements

A checkpoint claiming BMF-011 conformance SHALL demonstrate at least:

1. a generic discovery projection can enter passive research candidacy;
2. candidate path is exactly RX then ADEL;
3. research candidacy is capability-first;
4. unknown future capability identifiers remain accepted;
5. descriptor evidence is preserved;
6. candidate identity is deterministic;
7. candidate ordering is deterministic;
8. no `ResearchRequest` is imported or materialized by ingress;
9. non-SEARCH research capability escalation fails closed;
10. path escalation fails closed;
11. network escalation fails closed;
12. trust, installation, activation, authorization, execution, and truth escalation fail closed;
13. ingress requires no network or external process;
14. existing RX and ADEL governed stages remain separate;
15. BordingMap point `BMF-011` is explicitly assessed with evidence.

## Final invariant

> UNKNOWN TECHNOLOGY MAY BECOME A RESEARCH CANDIDATE WITHOUT BECOMING TRUSTED, INSTALLED, ACTIVATED, AUTHORIZED, EXECUTED, OR TRUE.
