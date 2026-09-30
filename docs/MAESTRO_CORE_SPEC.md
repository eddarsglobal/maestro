# MAESTRO CORE v0.1 — Kernel Specification

## 1. Purpose

MAESTRO is not Council 19.

MAESTRO is the conductor that turns human intent into governed APTE missions.

The kernel must remain independent of model vendors.

## 2. Constitutional invariants

### INV-EX-01 — Lifecycle authority
Only EX changes canonical mission state.

### INV-AY-01 — System verdict authority
Only AY may issue a SYSTEM verdict.

### INV-DOMAIN-01 — Domain verdicts
Every Council other than AY emits DOMAIN verdicts only.

### INV-TX-01 — Durable commit
TX may commit durable project state only after:
1. AY SYSTEM JUSTE;
2. EX commit authorization.

### INV-ROUTE-01 — Routing
All governed Council handoffs route through EX.

### INV-OP-RX-01 — Breakout
OP detects/recommends breakout. EX activates RX. RX returns evidence to EX.

### INV-ACTION-01 — Side effects
Model reasoning never grants itself permission to perform an external action.

## 3. Core planes

### Control Plane
Deterministic:
- lifecycle state;
- permissions;
- routing authorization;
- retries;
- commit authorization;
- action firewall.

### Intelligence Plane
Probabilistic:
- understanding;
- planning;
- semantic classification;
- content/code generation;
- hypothesis creation.

### Evidence Plane
Auditable:
- tests;
- diffs;
- scans;
- benchmarks;
- source evidence;
- user confirmations.

### Memory Plane
Durable:
- current project truth;
- ADRs;
- decisions;
- mission history;
- validated lessons.

## 4. Provider independence

A model provider is an implementation of the `ModelProvider` protocol.

No provider is allowed to redefine:
- Council authority;
- lifecycle transitions;
- permissions;
- verdict semantics;
- TX commit order.

## 5. v0.2 priorities

1. Persistent mission engine
2. Council context compiler
3. Execution DAG
4. Retry ledger / OP
5. Checkpoint/resume
6. Tool capability registry
7. Model policy per Council
8. Eval simulator
9. Mission replay
10. Cost/latency telemetry
