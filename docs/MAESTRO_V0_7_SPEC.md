# MAESTRO v0.7 — SELF-GOVERNING OPERATING SYSTEM

## Objective

Turn the autonomous runtime into a self-supervising operating system without turning it into an unbounded autonomous actor.

## New capabilities

### Event Sourcing
Runtime event history can be replayed into compact mission projections.

### Async Council Runtime
Independent Council execution requests can run concurrently through bounded asyncio concurrency.

### Distributed Leases / Heartbeats
Work items may be leased to workers with heartbeat-based expiry.

### Automatic Checkpoints
Runtime policy can checkpoint after N events or at critical states.

### Live OP Supervision
Failed work is immediately fed into OP's retry ledger. OP may recommend breakout; EX remains the activation authority for RX.

### Skill-to-DAG
Approved skills can compile directly into governed DAGs.

### Online Academy Feedback
Production-shaped scenario and shadow observations feed Academy without directly changing policy.

### Council Temperature
Councils have explicit runtime residency:
- HOT
- WARM
- COLD
- ABSENT

This protects MAESTRO's lightness invariant.

## Core principle

Self-governing does not mean self-authorizing.

MAESTRO may:
- supervise itself;
- checkpoint itself;
- detect dead loops;
- cool unused Councils;
- rehydrate needed Councils;
- feed Academy;
- recover runtime state.

MAESTRO may not:
- create authority without governance;
- bypass AY/EX;
- make protected side effects without approval;
- silently promote learned policies.
