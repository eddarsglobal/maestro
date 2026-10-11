# BM2 Cost Performance Privacy Locality Certification

Checkpoint: CPL0.1

## BM2-029 — Cost / Performance — PASS

Certified properties:

- mission-bound resource performance evidence
- measurable cost evidence
- measurable latency evidence
- measurable energy evidence
- explicit locality evidence
- measurable reliability evidence
- measurable outcome evidence
- explicit privacy evidence
- dedicated evidence reference for every metric
- energy is independent from cost
- energy is independent from latency
- metric evidence identity is deterministic
- resource optimization is deterministic
- outcome evidence participates in ranking
- reliability evidence participates in ranking
- privacy evidence participates in ranking
- energy evidence participates in ranking
- cost evidence participates in ranking
- latency evidence participates in ranking
- optimization grants no trust
- optimization grants no activation authority
- optimization grants no execution authority
- optimization grants no effect authority
- optimization grants no network authority
- optimization transfers no mission authority
- optimization asserts no system truth

## BM2-030 — Privacy / Locality — PASS

Certified properties:

- mission execution policy is bound to mission contract
- mission planning can explicitly prefer local execution
- mission planning can explicitly prefer offline execution
- mission planning can explicitly prefer private execution
- mission planning can explicitly require local execution
- mission planning can explicitly require offline execution
- mission planning can explicitly require private execution
- minimum privacy score is explicit
- minimum reliability is explicit
- maximum cost is explicit
- maximum latency is explicit
- maximum energy is explicit
- local and offline are distinct
- local and private are distinct
- offline and private are distinct
- hard constraints are evaluated before optimization
- remote-only resource fails a local-required mission
- online-only resource fails an offline-required mission
- non-private resource fails a private-required mission
- insufficient privacy fails closed
- excessive cost fails closed
- excessive latency fails closed
- excessive energy fails closed
- insufficient reliability fails closed
- no eligible resource fails closed
- fail-closed does not choose best available anyway
- soft preferences affect deterministic ranking
- selection remains authority-neutral

## BordingMap 2.0 state

TOTAL: 32

PASS: 30

DEFERRED: 2

BLOCKED: 0

MISSING: 0

NEXT: BM2-031

PROJECT_COMPLETE: FALSE

## Constitutional separations

OPTIMIZATION METRIC != AUTHORITY

BETTER SCORE != EXECUTION AUTHORIZATION

METRIC VALUE != SYSTEM TRUTH

LOW COST != LOW ENERGY

LOW LATENCY != LOW ENERGY

PREFERENCE != REQUIREMENT

PREFERENCE != AUTHORIZATION

NO ELIGIBLE RESOURCE != USE BEST AVAILABLE ANYWAY

LOCAL != OFFLINE

OFFLINE != LOCAL

LOCAL != PRIVATE

OFFLINE != PRIVATE

PRIVATE != TRUSTED

INELIGIBLE != SUBOPTIMAL

SUFFICIENCY != OPTIMIZATION

SELECTED != AUTHORIZED

OPTIMAL != AUTHORITATIVE

OPTIMIZATION != AUTHORIZATION

RESOURCE SELECTED != RESOURCE EXECUTED
