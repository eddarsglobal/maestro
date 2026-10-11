# MAESTRO Governed Council Expansion Constitution

## Scope

CEX0.1 governs:

- BM2-008 Council Gap
- BM2-009 Dynamic Council

It connects mission capability demand to the already existing
Council capsule and dynamic-registry lifecycle.

It does not replace the existing DynamicCouncilRegistry.

## CEX-01 — Council gaps are explicit evidence

A Council gap SHALL be derived from:

- explicit mission capability demand
- explicit existing capability coverage

The exact missing capability set SHALL be content-bound.

MISSING CAPABILITY != COUNCIL AUTHORIZED.

GAP DETECTED != COUNCIL INSTALLED.

## CEX-02 — No gap means no proposal

A dynamic Council proposal SHALL require an explicit non-empty
Council capability gap.

NO GAP != DYNAMIC COUNCIL REQUIRED.

EXISTING COVERAGE != NEW COUNCIL JUSTIFICATION.

## CEX-03 — Proposals bind the originating gap

Every Council proposal SHALL bind:

- mission capability-demand identity
- Council-gap identity
- proposed Council identity
- primary authority
- missing capabilities
- triggers
- cannot-own boundaries

PROPOSAL != APPROVAL.

PROPOSAL != INSTALLATION.

PROPOSAL != ACTIVATION.

## CEX-04 — Genesis Councils remain immutable

A dynamic proposal SHALL NOT replace or impersonate a Genesis Council.

GENESIS COUNCIL != DYNAMIC COUNCIL.

DYNAMIC COUNCIL != CONSTITUTIONAL AUTHORITY EXPANSION.

## CEX-05 — Capsule projection is governed

A proposal MAY project to the existing CouncilCapsuleManifest format.

Projection SHALL preserve proposal, gap and demand lineage.

CAPSULE CREATED != CAPSULE INSTALLED.

CAPSULE STORED != CAPSULE AUTHORIZED.

## CEX-06 — Shadow and evaluation precede eligibility

A PROPOSED capsule SHALL NOT become installation-eligible.

Installation eligibility requires an existing SHADOW or APPROVED
capsule state plus explicit evaluation evidence.

SHADOW != APPROVED.

EVALUATED != AUTHORIZED.

EVALUATION PASS != INSTALLATION EXECUTED.

## CEX-07 — AY and EX remain mandatory

Dynamic Council lifecycle SHALL preserve:

- AY validation
- EX authorization

Missing or failed authority evidence SHALL fail closed.

AY VALIDATED != EX AUTHORIZED.

EX AUTHORIZED != INSTALLED.

## CEX-08 — Human governance remains mandatory

Dynamic Council installation eligibility SHALL require explicit
human governance approval in addition to evaluation, AY and EX.

AUTONOMY != SELF-INSTALLATION.

COUNCIL PROPOSED != HUMAN APPROVED.

HUMAN APPROVED != ACTIVATED.

## CEX-09 — Eligibility is not installation authority

CEX0.1 MAY determine INSTALL_ELIGIBLE.

CEX0.1 SHALL NOT:

- install a Council
- activate a Council
- execute a Council
- mutate the dynamic registry
- replace a Genesis Council
- claim system truth

INSTALL_ELIGIBLE != INSTALLED.

INSTALLED != ACTIVATED.

ACTIVATED != EXECUTION AUTHORIZED.

## CEX-10 — Existing DynamicCouncilRegistry owns installation

The existing DynamicCouncilRegistry remains the downstream
operational installation boundary.

Its existing requirements remain mandatory:

- Genesis replacement denied
- SHADOW lifecycle requirement
- evaluation PASS
- AY validation
- EX authorization
- human governance approval

CEX assessment evidence MAY feed that boundary through future
explicit integration.

CEX0.1 itself remains passive.

## Canonical boundary

MISSION CAPABILITY DEMAND
        |
        +
EXISTING COUNCIL COVERAGE
        |
        v
COUNCIL GAP ASSESSMENT
        |
        +---- NO GAP
        |
        +---- GAP PRESENT
                 |
                 v
          COUNCIL PROPOSAL
                 |
                 v
          CAPSULE PROJECTION
                 |
                 v
              SHADOW
                 |
                 v
            EVALUATION
                 |
                 v
                AY
                 |
                 v
                EX
                 |
                 v
       HUMAN GOVERNANCE
                 |
                 v
        INSTALL_ELIGIBLE
                 |
                 v
         BOUNDARY STOPS
                 |
                 v
 EXISTING DYNAMIC REGISTRY
 OWNS GOVERNED INSTALLATION

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

## Final invariant

MAESTRO MAY DETECT A COUNCIL CAPABILITY GAP, PRODUCE A
GOVERNED DYNAMIC COUNCIL PROPOSAL, PROJECT IT INTO THE
EXISTING CAPSULE FORMAT AND DETERMINE INSTALLATION ELIGIBILITY
ONLY AFTER SHADOW, EVALUATION, AY, EX AND HUMAN GOVERNANCE,
WITHOUT CEX0.1 ITSELF INSTALLING, ACTIVATING OR EXECUTING
THE COUNCIL.
