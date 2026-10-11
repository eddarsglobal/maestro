# BM2 Experience Learning Promotion Certification

Checkpoint: ELP0.1

## BM2-024 — Experience Capture — PASS

Certified properties:

- experience binds durable mission checkpoint
- experience binds checkpoint SHA-256
- experience binds mission contract
- experience binds mission plan
- experience binds routing plan
- experience binds governed mission verdict
- UNKNOWN mission verdict cannot become experience
- successful experience requires ACCEPTED mission verdict
- successful experience requires verified-result reference
- failure experience requires failure evidence
- retry evidence is captured
- absence of retries can be represented explicitly
- routing quality is captured
- resource performance is captured
- resource quality is captured
- resource reliability is captured
- resource cost is captured
- resource latency is captured
- human corrections are provenanced
- evidence references are explicit
- total cost is captured
- total latency is captured
- experience is frozen/immutable
- experience identity is deterministic
- experience digest is SHA-256
- experience grants no learning authority
- experience grants no mutation authority

## BM2-025 — Learning Boundary — PASS

Certified properties:

- learning candidates derive only from immutable experience evidence
- at least two distinct support experiences are required
- support experience IDs are explicit
- counter-experience IDs are explicit
- source experience SHA-256 digests are bound
- candidate identity is deterministic
- candidate cannot mutate policy
- candidate cannot mutate memory authority
- candidate cannot mutate routing authority
- candidate cannot mutate Council authority
- candidate cannot mutate Core semantics
- candidate cannot change production behavior
- candidate cannot authorize promotion
- LEARN != PROMOTE
- PROPOSE != APPROVE

## BM2-026 — Promotion — PASS

Certified properties:

- promotion evaluation binds exact learning candidate
- minimum support threshold is explicit
- minimum evaluation sample count is explicit
- baseline score is explicit
- candidate score is explicit
- explicit comparison evidence is required
- replay score is explicit
- shadow success rate is explicit
- regression count is explicit
- minimum improvement is explicit
- rollback reference is mandatory
- AY validation evidence is mandatory
- EX authorization evidence is mandatory
- UNKNOWN AY/EX evidence yields UNKNOWN
- explicit AY/EX failure yields REJECTED
- insufficient support yields REJECTED
- insufficient samples yields REJECTED
- replay failure yields REJECTED
- shadow failure yields REJECTED
- regression failure yields REJECTED
- no measurable improvement yields REJECTED
- complete evidence may yield PROMOTION_ELIGIBLE
- PROMOTION_ELIGIBLE does not mutate policy
- PROMOTION_ELIGIBLE does not activate production
- PROMOTION_ELIGIBLE does not execute
- PROMOTION_ELIGIBLE does not assert system truth
- existing governed promotion and activation remain downstream

## BordingMap 2.0 state

TOTAL: 32

PASS: 26

DEFERRED: 6

BLOCKED: 0

MISSING: 0

NEXT: BM2-027

PROJECT_COMPLETE: FALSE

## Constitutional separations

EXPERIENCE != RAW EXECUTION LOG

OBSERVATION != VERIFIED EXPERIENCE

EXECUTION SUCCESS != VERIFIED EXPERIENCE

EXPERIENCE != LEARNING AUTHORITY

EXPERIENCE != POLICY

LEARNING CANDIDATE != LEARNED POLICY

LEARNING CANDIDATE != PRODUCTION BEHAVIOR

LEARN != PROMOTE

PROPOSE != APPROVE

CANDIDATE != AUTHORITY

EVALUATED != PROMOTED

BETTER SCORE != AUTHORITY

PROMOTION POSSIBLE != PROMOTION SAFE

PROMOTION READY != ACTIVATED

PROMOTION_ELIGIBLE != PROMOTED

PROMOTED != ACTIVATED

ACTIVATED != SYSTEM TRUTH
