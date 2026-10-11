# BM2 Governed Mission Plan Certification

Checkpoint: GMP0.1

## BM2-013 — Plan Synthesis — PASS

Certified properties:

- plan binds exact mission contract
- plan binds Council graph
- plan binds capability graph
- plan binds resource selection
- every required capability appears exactly once
- every node binds owning Council
- every node binds selected resource
- dependencies are explicit
- unknown dependencies fail closed
- self-dependencies fail closed
- cycles fail closed
- acceptance evidence is explicit
- retry policy is explicit
- recovery boundary is explicit
- deterministic plan identity
- plan construction requests no execution

## BM2-014 — Plan Validation — PASS

Certified properties:

- AY validation evidence is explicit
- relevant Council validation evidence is explicit
- mission acceptance criteria are explicit
- plan-invariant evidence is explicit
- incomplete evidence yields UNKNOWN
- UNKNOWN evidence never becomes eligible
- explicit FAIL yields REJECTED
- complete PASS evidence yields EXECUTION_ELIGIBLE
- execution eligibility grants no execution authority
- validation grants no system-truth authority

## BM2-015 — Effect Budget — PASS

Certified properties:

- effect declarations are explicit
- permission declarations are explicit
- tool-call budget is explicit
- cost budget is explicit
- latency budget is explicit
- network allowance is explicit
- filesystem-write allowance is explicit
- sandbox requirement is explicit
- network effects require NETWORK permission
- filesystem writes require FILESYSTEM_WRITE permission
- external effects require sandbox boundary
- effect declaration grants no effect authorization
- permission declaration grants no permission
- plan validation grants no network authority
- plan validation grants no filesystem-write authority
- existing downstream DAG/Sandbox/Effect mechanisms remain separate

## BordingMap 2.0 state

TOTAL: 32

PASS: 15

DEFERRED: 17

BLOCKED: 0

MISSING: 0

NEXT: BM2-016

PROJECT_COMPLETE: FALSE

## Constitutional separations

PLAN CREATED != PLAN AUTHORIZED

NODE CREATED != NODE EXECUTED

DAG VALID != DAG EXECUTED

NODE READY != NODE EXECUTED

OUTPUT PRODUCED != ACCEPTANCE PROVEN

RETRY POLICY != RETRY EXECUTION

EFFECT DECLARED != EFFECT AUTHORIZED

PERMISSION DECLARED != PERMISSION GRANTED

SANDBOX REQUIRED != SANDBOX EXECUTED

EXECUTION_ELIGIBLE != EXECUTION_AUTHORIZED

PLAN VALIDATED != EFFECT AUTHORIZED

PLAN SYNTHESIS != RUNTIME EXECUTION
