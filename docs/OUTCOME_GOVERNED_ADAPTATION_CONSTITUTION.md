# MAESTRO v1.0.9 — OUTCOME-GOVERNED ADAPTATION

## Core law

> OUTCOMES MAY INFORM ADAPTATION. OUTCOMES MAY NOT AUTHORIZE ADAPTATION.

Verified outcomes are evidence. They are not authority.

Canonical flow:

`VERIFIED OUTCOMES → ATTRIBUTABLE PATTERN → ADAPTATION CANDIDATE → SHADOW → ACADEMY → PROMOTION EVIDENCE → AY + EX GOVERNANCE → ACTIVE POLICY`

A single outcome cannot create an active policy. Counter-evidence remains visible. Outcome-derived candidates cannot expand constitutional authority, tool permissions, Council authority, TX authority, or human approval boundaries.

## Subject-binding rule

An adaptation pattern must refer to one concrete adaptation subject.

Examples:

- `RESOURCE` → exact `resource_id`;
- `TOOL` → explicit `tool_id` or `tool_name`;
- `CONTEXT` → explicit `context_id` or `context_ref`;
- `STRATEGY` → explicit `strategy_id` or `strategy_key`.

Evidence concerning different subjects must not be merged into one learning pattern.

> APTE-OGA-11 — ADAPTATION PATTERNS MUST BE BOUND TO A CONCRETE SUBJECT.

## Persistent verified-outcome memory

Outcome Intelligence memory is durable evidence, not transient process state.

A restart must reload persisted verified outcomes before adaptation analysis.
Outcome-Governed Adaptation must also reload its own candidate ledger so that
restart cannot silently erase candidate provenance or recreate duplicate
candidates.

Cross-version imports may copy verified outcomes into the new runtime only if:

- the original `outcome_id` is preserved;
- `ay_verified` remains true;
- duplicates are ignored by ID;
- the imported outcome is not rewritten as new evidence;
- import grants no activation authority.

> APTE-OGA-12 - VERIFIED OUTCOME MEMORY MUST SURVIVE RESTART.

> APTE-OGA-13 - CROSS-VERSION OUTCOME IMPORT MUST PRESERVE PROVENANCE AND IDS.

## Durable candidate lifecycle

Candidate lifecycle states such as `ELIGIBLE`, `SHADOW`, `EVALUATING`, and
`PROMOTION_READY` are governance-relevant state. The candidate ledger keeps an
append-only snapshot history while its logical view resolves to the latest
snapshot for each `candidate_id`. A restart must not move a candidate backward.

> APTE-OGA-14 — CANDIDATE LIFECYCLE TRANSITIONS MUST SURVIVE RESTART.

## No-gain terminal disposition

A candidate that has completed SHADOW/Academy evaluation must not remain
indefinitely in `EVALUATING` when it is proven behaviorally equivalent to the
current baseline and produces no measurable improvement.

A no-gain terminal disposition requires all of the following:

- candidate status is `EVALUATING`;
- baseline and candidate are behaviorally equivalent for the evaluated scope;
- replay delta is zero within a deterministic epsilon;
- improvement count is zero;
- regression count is zero;
- Academy does not recommend the candidate.

When all conditions hold, the candidate becomes `REJECTED` with terminal reason
`NO_GAIN_REDUNDANT`. The transition is persisted in the append-only candidate
ledger. This is not a failure of the resource; it means the proposed adaptation
adds no value over current behavior.

> APTE-OGA-15 - NO-GAIN ADAPTATIONS MUST TERMINATE WITHOUT PROMOTION.

## Learning-grade evaluation provenance

Diagnostic model evaluation and learning-grade evaluation are not equivalent.

A candidate may become `PROMOTION_READY` through the governed OGA engine only
when evaluation evidence is bound to an immutable deterministic profile and
records semantic correctness separately from format compliance.

Minimum learning-grade requirements include:

- explicit provider and inference route;
- `temperature = 0`;
- explicit reproducibility seed;
- bounded generation budget;
- semantic correctness measurement;
- format compliance measurement;
- zero semantic regressions;
- zero format regressions;
- minimum evaluation sample count;
- success thresholds satisfied.

A higher aggregate Academy score without these properties remains diagnostic
evidence and must not teach policy activation.

> APTE-OGA-16 - LEARNING-GRADE EVALUATION REQUIRES DETERMINISTIC PROFILE AND SEMANTIC/FORMAT EVIDENCE.

## Native execution-profile binding

A learning-grade evaluation profile must govern the actual inference request,
not merely describe intended settings after execution.

The provider-neutral Sovereign request carries an immutable execution profile.
Provider adapters translate that profile into provider-specific controls while
preserving its profile reference in response metadata.

This preserves the authority boundary:

`OGA evaluation policy -> Sovereign execution contract -> replaceable provider`

and prevents provider defaults from silently changing learning evidence.

> APTE-OGA-17 - LEARNING-GRADE EVALUATION PROFILE MUST GOVERN THE ACTUAL INFERENCE REQUEST.

## Academy learning-grade evidence binding

Academy learning-grade evaluation must verify that the execution profile
declared by governance is the same profile actually reported by the
intelligence adapter.

Semantic correctness and format compliance remain separate evidence
dimensions. A scenario is learning-grade successful only when:

- the deterministic execution profile is bound to the request;
- the returned profile reference matches;
- deterministic execution is confirmed;
- semantic correctness passes;
- format compliance passes.

Caching may reuse an identical resource/scenario/profile execution, but it may
not change the policy identity presented to Academy.

> APTE-OGA-18 - ACADEMY LEARNING-GRADE EVIDENCE MUST VERIFY EXECUTION-PROFILE PROVENANCE.

