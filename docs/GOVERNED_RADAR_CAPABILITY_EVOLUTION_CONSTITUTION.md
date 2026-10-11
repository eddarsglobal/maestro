# MAESTRO Governed Radar Capability Evolution Constitution

## Scope

RCE0.1 governs:

- BM2-027 Radar Loop
- BM2-028 Capability Evolution

It provides a Phase 2 evidence lineage over existing Technology Radar,
research, capability-candidate, integration-adapter and architecture-evolution
primitives.

RCE0.1 is passive.

## RCE-01 — Discovery is observation only

A technology observation SHALL contain:

- subject
- source kind
- source reference
- claims
- capability terms

Discovery grants no trust, installation, activation, authorization or
execution authority.

DISCOVER != TRUST.

DISCOVER != INSTALL.

DISCOVER != ACTIVATE.

DISCOVER != AUTHORIZE.

## RCE-02 — Human discovery is first-class evidence ingress

A human may introduce a technology observation.

Human discovery SHALL enter the same governed Radar path as other
observations.

HUMAN OBSERVATION != SYSTEM TRUTH.

HUMAN DISCOVERY != TRUST DECISION.

## RCE-03 — Research evidence remains evidence

Research findings SHALL bind the exact originating observation.

Research MAY verify, reject or remain unknown.

Research SHALL NOT silently add unrelated capability claims.

RESEARCHED != TRUSTED.

VERIFIED CLAIM != INSTALLED CAPABILITY.

## RCE-04 — Unknown or rejected research cannot become capability candidate

Only VERIFIED research evidence may produce a capability candidate.

UNKNOWN SHALL fail closed.

REJECTED SHALL fail closed.

UNKNOWN != VERIFIED.

REJECTED != CAPABILITY.

## RCE-05 — Capability evolution requires a real capability gap

Candidate derivation SHALL compare researched capability terms with existing
MAESTRO capabilities.

Only missing capabilities may enter the evolution candidate.

KNOWN CAPABILITY != MISSING CAPABILITY.

TECHNOLOGY != CAPABILITY.

## RCE-06 — Capability candidate is passive

A capability candidate SHALL NOT:

- grant trust
- request installation
- request activation
- assert authorization
- request execution
- mutate ontology
- alter constitutional identity
- mutate Core

CAPABILITY CANDIDATE != INSTALLED CAPABILITY.

CAPABILITY CANDIDATE != TRUSTED RESOURCE.

## RCE-07 — Missing capability may produce governed evolution proposal

A verified capability gap MAY produce one of:

- adapter proposal
- integration proposal
- architecture-evolution proposal

Proposal type is evidence metadata, not authority.

PROPOSAL != INSTALLATION.

PROPOSAL != ACTIVATION.

## RCE-08 — Evolution proposals preserve ontology and identity

Architecture evolution MAY propose implementation changes.

It SHALL NOT silently alter:

- MAESTRO constitutional identity
- provider/model independence
- Council authority model
- Core ontology
- sovereignty laws

ARCHITECTURE PROPOSAL != ONTOLOGY MUTATION.

NEW TECHNOLOGY != NEW CONSTITUTIONAL IDENTITY.

## RCE-09 — Provider and technology names remain data

Concrete technology identities SHALL remain observation/candidate data.

No technology name SHALL become required constitutional knowledge.

TECHNOLOGY NAME != CORE IDENTITY.

ADAPTER DATA != CONSTITUTIONAL DEPENDENCY.

## RCE-10 — Existing downstream governance remains authoritative

RCE0.1 SHALL NOT:

- install software
- download software
- select a provider for execution
- activate resources
- execute tools
- authorize effects
- authorize network
- authorize learning
- authorize promotion
- mutate Core
- assert system truth

Existing Radar, research review, capability integration, sandbox,
supply-chain, AY, EX and governed activation remain downstream.

DISCOVER != TRUST != INSTALL != ACTIVATE != AUTHORIZE.

## Canonical Radar loop

TECHNOLOGY OBSERVATION
        |
        v
RADAR / RESEARCH
        |
        v
RESEARCH EVIDENCE
        |
        +---- UNKNOWN -> STOP
        |
        +---- REJECTED -> STOP
        |
        +---- VERIFIED
                  |
                  v
        CAPABILITY COMPARISON
                  |
          +-------+-------+
          |               |
          v               v
      ALREADY KNOWN    MISSING
          |               |
          v               v
         STOP      CAPABILITY CANDIDATE
                          |
                          v
                 EVOLUTION PROPOSAL
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
           ADAPTER   INTEGRATION  ARCHITECTURE
              |
              v
        BOUNDARY STOPS

## Constitutional separations

DISCOVER != TRUST

DISCOVER != INSTALL

DISCOVER != ACTIVATE

DISCOVER != AUTHORIZE

HUMAN OBSERVATION != SYSTEM TRUTH

HUMAN DISCOVERY != TRUST DECISION

RESEARCHED != TRUSTED

VERIFIED CLAIM != INSTALLED CAPABILITY

UNKNOWN != VERIFIED

REJECTED != CAPABILITY

KNOWN CAPABILITY != MISSING CAPABILITY

TECHNOLOGY != CAPABILITY

CAPABILITY CANDIDATE != INSTALLED CAPABILITY

CAPABILITY CANDIDATE != TRUSTED RESOURCE

PROPOSAL != INSTALLATION

PROPOSAL != ACTIVATION

ARCHITECTURE PROPOSAL != ONTOLOGY MUTATION

NEW TECHNOLOGY != NEW CONSTITUTIONAL IDENTITY

TECHNOLOGY NAME != CORE IDENTITY

ADAPTER DATA != CONSTITUTIONAL DEPENDENCY

DISCOVER != TRUST != INSTALL != ACTIVATE != AUTHORIZE

## Final invariant

MAESTRO MAY ACCEPT HUMAN OR AUTOMATED TECHNOLOGY OBSERVATIONS, RESEARCH
THEM, DERIVE VERIFIED CAPABILITY GAPS AND PRODUCE GOVERNED ADAPTER,
INTEGRATION OR ARCHITECTURE-EVOLUTION PROPOSALS, WHILE EVERY CONCRETE
TECHNOLOGY REMAINS DATA AND DISCOVERY NEVER SILENTLY BECOMES TRUST,
INSTALLATION, ACTIVATION, AUTHORIZATION, EXECUTION, ONTOLOGY MUTATION
OR CONSTITUTIONAL IDENTITY.
