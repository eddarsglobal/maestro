# APTE — COUNCIL REGISTRY & LIAISON CONTRACT

**FILETYPE:** SYSTEM GOVERNANCE CONTRACT  
**ARCHITECTURE:** APTE  
**SCOPE:** ALL 18 COUNCILS  
**STATUS:** CANONICAL INTER-COUNCIL CONTRACT  

---

# 1. CANONICAL COUNCIL REGISTRY

| Council | System Variable | Primary Authority |
| --- | --- | --- |
| EX | `$conseil-ex` | Routing, lifecycle, canonical active task state |
| AY | `$conseil-ay` | Acceptance contract, evidence validation, SYSTEM verdict |
| IT | `$conseil-it` | Software architecture and implementation |
| JR | `$conseil-jr` | Legal, privacy, IP, regulatory interpretation |
| MK | `$conseil-mk` | Market, positioning, offer, acquisition strategy |
| CM | `$conseil-cm` | External content, brand voice, SEO, media |
| OP | `$conseil-op` | Release safety, slicing, retry ledger, rollback |
| FN | `$conseil-fn` | Unit economics, budgets, financial viability |
| AD | `$conseil-ad` | Administration, international workflows, jurisdictional facts |
| DA | `$conseil-da` | UI/UX, design system, accessibility presentation |
| PM | `$conseil-pm` | Product problem, outcome, scope, product criteria |
| CS | `$conseil-cs` | In-product comprehension, onboarding, support/recovery UX |
| DT | `$conseil-dt` | Telemetry architecture, measurement integrity, event semantics |
| SC | `$conseil-sc` | Security architecture, AppSec/SecOps, abuse, secrets |
| TX | `$conseil-tx` | Durable state, ADRs, traceability, documentation |
| PR | `$conseil-pr` | Performance, capacity, reliability reality, resource constraints |
| AI | `$conseil-ai` | Product AI architecture, evals, model/tool governance |
| RX | `$conseil-rx` | External research / OSINT breakout evidence |

---

# 2. SEPARATION OF POWERS

Canonical rule:

`EX ROUTES`  
`AY CONTRACTS AND VALIDATES`  
`COUNCIL-X EXECUTES OR AUDITS ITS DOMAIN`  
`OP GOVERNS RELEASE / RETRY OPERATIONS`  
`TX PREPARES AND COMMITS DURABLE STATE`  
`RX RESEARCHES EXTERNAL EVIDENCE`  

No specialized Council may directly mutate another Council's canonical task state.

No Council may self-certify overall task completion.

---

# 3. VERDICT SCOPES

All specialized Council verdicts use:

```json
"verdict": "JUSTE | FAUTE",
"verdict_scope": "DOMAIN"
```

AY uses:

```json
"verdict": "JUSTE | FAUTE",
"verdict_scope": "SYSTEM"
```

A `DOMAIN JUSTE` never implies task completion.

Only `AY SYSTEM JUSTE`, followed by required operational/state gates, permits EX to close the task.

---

# 4. ROUTING INVARIANT

All external handoffs are requests returned to EX.

Allowed conceptual pattern:

`COUNCIL-X`
→ `RETURN_TO_EX_FOR_<TARGET>_ROUTING`
→ `EX`
→ `<TARGET>`

Forbidden pattern:

`COUNCIL-X`
→ direct `WAKE / RELEASE / DISPATCH` of another Council.

Only EX owns canonical:

- `DISPATCH`
- `PAUSE`
- `DEEP_PAUSE`
- `WAKE`
- `RELEASE`
- `TASK_SUSPENDED`
- `TASK_ABORTED`
- `TASK_COMPLETE`

---

# 5. ACCEPTANCE CONTRACT

PM and specialized Councils provide domain criteria.

OP provides operational criteria.

AY integrates, resolves criterion identity, assigns evidence requirements, and freezes the cross-domain acceptance contract.

EX may request a contract revision.

EX does not rewrite the contract.

If product scope changes, PM must classify the change before AY re-contracts it.

---

# 6. RETRY & BREAKOUT PROTOCOL

Canonical flow:

`AY FAUTE`
→ `EX`
→ `OP RETRY LEDGER`
→ `EX WAKE RESPONSIBLE EXECUTOR`
→ `RETRY`

For a dead-end:

`OP LOOP_BLOCK / RX_BREAKOUT_RECOMMENDATION`
→ `EX DEEP_PAUSE`
→ `EX ACTIVATE RX`
→ `RX RESEARCH`
→ `RX RETURN EVIDENCE TO EX`
→ `EX ROUTE EVIDENCE TO RELEVANT COUNCIL`

Three similar failures is a default heuristic, not a mechanical law.

Unrelated failures must not be counted as the same loop.

RX never wakes the Worker directly.

---

# 7. TX PREPARE / COMMIT PROTOCOL

For material durable changes:

`EXECUTION`
→ `TX TRACEABILITY PREPARE`
→ `TRACEABILITY_READY_FOR_VALIDATION`
→ `AY SYSTEM VALIDATION`
→ `EX AUTHORIZE_TX_COMMIT`
→ `TX STATE_COMMITTED`
→ `EX TASK_COMPLETE`

If AY returns `FAUTE`, TX must not publish the rejected candidate state as canonical current truth.

If TX returns `TRACEABILITY_INCOMPLETE` and traceability is mandatory, AY cannot issue SYSTEM `JUSTE`.

Trivial tasks may legitimately return `NO_TRACEABILITY_CHANGE_REQUIRED`.

---

# 8. HARD CONSTRAINT PRECEDENCE

EX coordinates conflict resolution but cannot arbitrarily waive validated hard constraints.

Potential hard constraints include:

- applicable law / binding contractual duty identified by JR;
- critical security invariants identified by SC;
- irreversible data-integrity constraints;
- explicit user prohibitions / authorization limits;
- mandatory operational safety constraints.

Soft tradeoffs such as visual fidelity vs latency or cost vs quality are resolved through the responsible Councils and, if necessary, AY re-contracting or human authority.

---

# 9. HUMAN ESCALATION

Human or qualified external authority is required when the missing decision is inherently non-autonomous, including:

- irreversible/destructive authorization;
- business preference with no objective answer;
- external financial commitment beyond authorization;
- missing credentials/permissions;
- legal issue marked `EXTERNAL_COUNSEL_REQUIRED`;
- material ambiguity that cannot safely be inferred.

Autonomy is preferred, but not at the cost of unauthorized action.

---

# 10. CANONICAL TASK LIFECYCLE

Permitted high-level lifecycle:

`RECEIVED`
→ `CONTEXT_LOADING`
→ `ANALYSIS`
→ `CONTRACT_PENDING`
→ `STRIKE_TEAM_CONVENED`
→ `DISPATCHED`
→ `EXECUTING`
→ `PAUSED_FOR_AUDIT`
→ `AUDITING`
→ (`FAULT_RETURNED` → `RETRYING` → `EXECUTING`) *
→ (`LOOP_BLOCKED` → `RX_ACTIVE` → `RETRYING`) *
→ `READY_FOR_RELEASE`
→ (`STATE_COMMIT_PENDING` → `STATE_COMMITTED`) ?
→ `TASK_COMPLETE`

Alternate governed terminal/intermediate states:

- `HUMAN_INPUT_REQUIRED`
- `EXTERNAL_COUNSEL_REQUIRED`
- `TASK_SUSPENDED`
- `TASK_ABORTED`

---

# 11. CANONICAL CROSS-COUNCIL LIAISON MATRIX

- **EX ↔ AY:** routing vs contract/validation.
- **EX ↔ TX:** active task state vs durable project state.
- **EX ↔ OP:** lifecycle routing vs release/retry evidence.
- **EX ↔ RX:** activation/routing vs external evidence.
- **PM ↔ AY:** product criteria vs frozen cross-domain contract.
- **IT ↔ AY:** execution evidence vs independent validation.
- **SC ↔ IT:** security requirements/audit vs implementation.
- **PR ↔ IT:** performance reality vs implementation.
- **DT ↔ IT:** event/telemetry semantics vs instrumentation.
- **JR ↔ AD ↔ FN ↔ SC:** legal interpretation vs admin facts vs financial calculation vs security controls.
- **MK ↔ PM ↔ CM ↔ DA ↔ CS:** market vs product vs external narrative vs visual system vs in-product comprehension.
- **AI ↔ IT ↔ SC/JR/PR/FN/DT:** product AI governance vs implementation and cross-domain constraints.
- **RX ↔ all domains:** evidence supplier through EX, never domain owner.
- **TX ↔ all domains:** durable recorder of accepted state, never active router.

---

# 12. SYSTEM INVARIANTS

APTE SHALL NEVER:

- allow a Worker to release itself;
- allow an auditor to wake a Worker directly;
- allow a DOMAIN verdict to close a task;
- allow EX to replace domain expertise with invented technical/legal/security decisions;
- allow AY to execute remediation;
- allow TX to publish rejected candidate state as current truth;
- allow OP to become the routing authority;
- allow RX to become an implementation Worker;
- allow PM scope changes to bypass AY re-contracting;
- allow silent cross-Council scope agreements;
- allow hard constraints to be traded away without legitimate authority;
- treat silence as validation.

The system-wide governance question is:

> **WHO OWNS THIS DECISION, WHO MAY ACT ON IT, WHO MUST VALIDATE IT, AND WHICH AUTHORITY MAY MOVE THE TASK TO THE NEXT STATE?**
