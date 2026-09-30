# MAESTRO v0.6 — AUTONOMOUS RUNTIME

## Objective

Turn MAESTRO from an adaptive kernel into a persistent, recoverable, distributed-ready runtime.

## New runtime planes

### Mission/Event Persistence
- durable latest mission snapshot;
- append-only runtime events;
- checkpoint-aware crash recovery.

### Scheduler / Work Queues
- priority queue;
- leasing;
- completion/failure/requeue;
- worker Council allowlists.

### Council Execution Adapters
Each Council may have a replaceable execution adapter.

The adapter executes Council work. It does not own global lifecycle authority.

### Provider Adapters
Models are provider-neutral runtime resources.

### Sandboxed Tool Runner
All tool calls cross:
`Council -> Sandbox -> Tool Registry -> Action Firewall -> Tool`

### Live Shadow Evaluation
Candidate policies can observe live decisions without becoming production policy.

### Skill Runtime
Approved skills compile into execution plans referencing Councils/strategies/tools.

### Distributed Worker Shape
Workers are registered with:
- ID
- Council allowlist
- capabilities
- runtime state

Workers do not own mission truth.

## Recovery

Preferred order:

```text
CHECKPOINT
  ↓ if unavailable/corrupt
MISSION STORE
  ↓
EVENT HISTORY FOR AUDIT
```

No recovered mission is silently marked complete.

## v0.6 non-goals

- not a Kubernetes deployment system;
- not an OS/container sandbox;
- not an unrestricted autonomous actor;
- not tied to a specific LLM provider;
- not a replacement for human authorization on A3/A4 actions.
