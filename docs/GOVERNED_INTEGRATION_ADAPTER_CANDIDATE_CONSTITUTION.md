# MAESTRO Governed Integration / Adapter Candidate Constitution

## Scope

This constitution governs BMF-020:

MAESTRO can propose integration or adapter candidates without implicitly activating them.

The BMF-020 boundary is proposal-only.

It consumes already governed capability candidates and may describe possible integration or adapter contracts without mutating registries, creating bindings, installing software, activating resources, authorizing execution, or changing Core architecture.

## IAP-01 — Capability candidacy precedes integration proposal

A governed integration or adapter proposal SHALL originate from an existing GovernedCapabilityCandidate.

No capability candidate SHALL mean no fabricated integration or adapter proposal.

CAPABILITY CANDIDATE != INTEGRATION PROPOSAL.

## IAP-02 — Integration proposals require an explicit interface contract

Every integration proposal SHALL identify an explicit generic interface contract.

The proposal SHALL describe a possible boundary.

It SHALL NOT create that boundary operationally.

PROPOSED INTERFACE != BOUND INTERFACE.

## IAP-03 — Adapter proposals are optional and explicit

An integration proposal MAY exist without an adapter proposal.

An adapter proposal SHALL require both:

- adapter kind
- resource contract

Partial adapter metadata SHALL fail closed.

## IAP-04 — Proposal lineage is preserved

Every integration and adapter proposal SHALL preserve:

- capability candidate identity
- landscape change identity
- current snapshot identity
- scope identity
- technology subject identity
- capability identity
- evidence identity
- source reference
- landscape evidence lineage

Proposal creation SHALL NOT sever evidence lineage.

## IAP-05 — Proposal identity is deterministic

Equivalent governed inputs SHALL produce equivalent proposal identities.

Ordering of equivalent requirement sets SHALL NOT fabricate a different semantic proposal.

Proposal collections SHALL be deterministically ordered.

## IAP-06 — External evidence remains unverified

Integration and adapter proposals derived from external research SHALL remain:

UNVERIFIED_EXTERNAL

PROPOSAL != VERIFIED FACT.

PROPOSAL != SYSTEM TRUTH.

## IAP-07 — Proposal is not registration or binding

INTEGRATION PROPOSAL != REGISTRY MUTATION
ADAPTER PROPOSAL != REGISTRATION
ADAPTER PROPOSAL != ADAPTER BINDING

BMF-020 SHALL NOT call or mutate DynamicAdapterRegistry.

BMF-020 SHALL NOT create AdapterBinding.

## IAP-08 — Proposal carries no operational authority

PROPOSAL != TRUST
PROPOSAL != INSTALL
PROPOSAL != ACTIVATE
PROPOSAL != AUTHORIZE
PROPOSAL != EXECUTE
PROPOSAL != CORE MUTATION

Any attempted downstream authority escalation SHALL fail closed.

## IAP-09 — BMF-020 remains separate from BMF-021

BMF-020 concerns integration and adapter proposals for already understood capability semantics.

BMF-021 concerns governed architecture-evolution proposals when the current capability ontology is insufficient.

INTEGRATION / ADAPTER PROPOSAL != ARCHITECTURE-EVOLUTION PROPOSAL.

BMF-020 SHALL NOT silently create BMF-021 authority or artifacts.

## IAP-10 — Proposal generation remains passive and technology-generic

The BMF-020 proposal boundary SHALL perform no:

- network access
- process launch
- external research
- persistence
- registry mutation
- adapter binding
- provider invocation
- installation
- activation
- authorization
- execution
- learning
- promotion
- Core mutation

Provider, model, runtime, operating-system, protocol, and hardware identities SHALL remain replaceable external data rather than constitutional identities.

## Canonical boundary

GOVERNED CAPABILITY CANDIDATE
        |
        v
EXPLICIT GENERIC INTERFACE CONTRACT
        |
        v
GOVERNED INTEGRATION CANDIDATE
        |
        +---- optional explicit adapter contract ----+
                                                    |
                                                    v
                                      GOVERNED ADAPTER CANDIDATE

The boundary stops before registration, binding, activation, execution, or architecture evolution.

## Final invariant

MAESTRO MAY PROPOSE HOW A GOVERNED CAPABILITY COULD BE INTEGRATED WITHOUT REGISTERING, BINDING, TRUSTING, INSTALLING, ACTIVATING, AUTHORIZING, EXECUTING, OR CHANGING ITS ARCHITECTURE.
