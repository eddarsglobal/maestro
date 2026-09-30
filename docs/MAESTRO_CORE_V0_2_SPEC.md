# MAESTRO CORE v0.2 — Execution Runtime Specification

## 1. DAG Engine

The graph models work dependencies, not conversational turn order.

A node has:
- `node_id`
- `council`
- `action`
- `criteria_ids`
- `depends_on`
- `state`
- `output`

Only EX may move a node into RUNNING or reset it for retry.

A Council may finish its own execution output, but canonical dispatch remains governed.

## 2. Council Context Compiler

The compiler enforces **least necessary context**.

Input:
- mission;
- Council assignment;
- dependency outputs;
- evidence;
- APTE authority registry.

Output:
- concise Council context.

It intentionally excludes:
- unrelated Council history;
- hidden model chain-of-thought;
- unrelated evidence;
- global project memory unless explicitly selected.

## 3. OP Retry Ledger

The ledger treats a loop as:

`same task + same worker + same criterion/failure signature + same strategy signature`

This prevents the old error of treating unrelated failures as one "three-strike" sequence.

The third materially equivalent failure produces:

`BREAKOUT_CANDIDATE`

It does **not** activate RX.

EX remains the activation authority.

## 4. Checkpoint / Resume

Checkpoint schema:
`maestro.checkpoint.v0.2`

A checkpoint stores:
- mission;
- DAG;
- OP ledger;
- evidence IDs;
- trace count;
- metadata;
- SHA-256 integrity digest.

Checkpoint persistence is runtime recovery state.
It is not equivalent to TX's approved durable project truth.

This distinction is intentional.

## 5. Tool Registry

Each tool has:
- name;
- capabilities;
- allowed Councils;
- side-effect level;
- policy approval requirement;
- human approval requirement.

A model cannot modify these permissions.

Tool execution always crosses the deterministic registry/firewall boundary.

## 6. Separation of checkpoint and TX memory

Checkpoint:
- runtime continuity;
- temporary execution state;
- resumability.

TX:
- validated durable project truth;
- ADRs;
- accepted decisions;
- release/state history.

A checkpoint may contain failed or unvalidated work.
TX current truth must not.

## 7. v0.2 exit criteria

- 18-Council registry preserved.
- No domain Council can issue SYSTEM verdict.
- No non-EX actor can transition mission state.
- DAG rejects cycles.
- OP ledger distinguishes strategy changes.
- Checkpoint detects tampering.
- Tool Registry prevents unauthorized Council/tool combinations.
- A3/A4 actions require deterministic approval gates.
