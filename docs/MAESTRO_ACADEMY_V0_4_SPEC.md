# MAESTRO v0.4 — ACADEMY

## Objective

ACADEMY gives MAESTRO the ability to measure its own weaknesses and construct a training program without granting it uncontrolled self-modification.

## Pipeline

```text
HISTORICAL EXPERIENCE / SYNTHETIC SCENARIOS
        ↓
MISSION SIMULATOR
        ↓
POLICY EXECUTION
        ↓
COUNCIL BENCHMARK
        ↓
WEAKNESS MAP
        ↓
CURRICULUM ENGINE
        ↓
TRAINING / SHADOW RUNS
        ↓
HISTORICAL REPLAY
        ↓
POLICY TOURNAMENT
        ↓
LEARNING CANDIDATE
        ↓
PROMOTION GATE
        ↓
AY VALIDATION
        ↓
EX AUTHORIZATION
```

## Measurements

ACADEMY measures:
- mission success;
- Council routing precision;
- Council routing recall;
- forbidden Council activation;
- required gate compliance;
- human approval behavior;
- evidence quality;
- retries;
- cost;
- latency.

## Weakness Map

Weaknesses are represented explicitly:

- task-family weakness;
- Council recall weakness;
- coverage gap;
- later: tool, model, context and retry-strategy weaknesses.

## Curriculum

The Curriculum Engine converts measured weaknesses into bounded practice plans.

A curriculum is not an active policy.

## Historical Replay

Candidate policy and baseline policy are executed against the same scenarios.

The replay report contains:
- baseline score;
- candidate score;
- delta;
- improvement count;
- regression count;
- exact regression scenarios.

## Shadow Tournament

Multiple policies may compete simultaneously.

Ranking prioritizes:
1. benchmark quality;
2. success;
3. lower retry count;
4. lower cost;
5. lower latency.

The winner is still only a recommendation.

## Lightness

ACADEMY is not kept fully resident.
Its large scenario corpus and result corpus are external binary objects.

The active Core only needs indexes and current evaluation aggregates.
