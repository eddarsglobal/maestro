# BM2 Council Expansion Certification

Checkpoint: CEX0.1

## BM2-008 — Council Gap — PASS

Certified properties:

- mission capability demand is explicit
- existing coverage is explicit
- exact missing capability set is deterministic
- no-gap state produces no proposal
- Council gap binds capability-demand identity
- Council gap grants no installation authority
- Council gap grants no activation authority
- Council gap grants no execution authority
- missing capability never fabricates an installed Council

## BM2-009 — Dynamic Council — PASS

Certified properties:

- proposal requires explicit Council gap
- proposal binds gap and demand lineage
- Genesis Council replacement is denied
- proposal projects to existing CouncilCapsuleManifest
- capsule lineage retains proposal/gap/demand identity
- PROPOSED requires shadow progression
- evaluation evidence is explicit
- AY validation is explicit
- EX authorization is explicit
- human governance approval is explicit
- failed lifecycle evidence rejects progression
- unknown lifecycle evidence fails closed
- INSTALL_ELIGIBLE is explicit
- INSTALL_ELIGIBLE does not install
- CEX does not activate
- CEX does not execute
- existing DynamicCouncilRegistry remains downstream
- existing dynamic Council registry tests pass
- existing registry requires SHADOW
- existing registry requires evaluation + AY + EX + human governance
- existing registry protects Genesis Councils

## BordingMap 2.0 state

TOTAL: 32

PASS: 9

DEFERRED: 23

BLOCKED: 0

MISSING: 0

NEXT: BM2-010

PROJECT_COMPLETE: FALSE

## Constitutional separations

MISSING CAPABILITY != COUNCIL AUTHORIZED

GAP DETECTED != COUNCIL INSTALLED

PROPOSAL != APPROVAL

PROPOSAL != INSTALLATION

PROPOSAL != ACTIVATION

GENESIS COUNCIL != DYNAMIC COUNCIL

CAPSULE CREATED != CAPSULE INSTALLED

SHADOW != APPROVED

EVALUATED != AUTHORIZED

AY VALIDATED != EX AUTHORIZED

EX AUTHORIZED != INSTALLED

AUTONOMY != SELF-INSTALLATION

INSTALL_ELIGIBLE != INSTALLED

INSTALLED != ACTIVATED

ACTIVATED != EXECUTION AUTHORIZED
