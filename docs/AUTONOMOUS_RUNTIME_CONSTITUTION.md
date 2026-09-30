# MAESTRO Autonomous Runtime Constitution

## AUTO-01 — Autonomy remains constitutional
Autonomous scheduling, execution and recovery do not bypass EX, AY, OP, TX, SC or JR authority.

## AUTO-02 — Work items are not authority
A queued work item is permission to execute only the action already authorized by the runtime contract.

## AUTO-03 — Workers are disposable
Workers may come and go. Canonical mission state lives outside workers.

## AUTO-04 — Crash recovery is deterministic
Mission/event/checkpoint state must allow MAESTRO to resume without inventing completed work.

## AUTO-05 — Provider adapters are replaceable
No provider SDK is allowed to become the architecture.

## AUTO-06 — Tool execution remains behind Tool Registry + Action Firewall
Council adapters cannot bypass sandbox/tool permissions.

## AUTO-07 — Shadow execution has no production side effects
Shadow policies may evaluate decisions but may not duplicate irreversible actions.

## AUTO-08 — Skills compile to governed work
Skills are reusable plans, not new authorities.

## AUTO-09 — Distributed workers preserve Council boundaries
A worker may execute only Councils in its explicit allowlist.

## AUTO-10 — Event history is append-only
Heavy artifacts may be stored by binary reference, but runtime history remains auditable.
