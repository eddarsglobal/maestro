from maestro.academy import (
    MaestroAcademy,
    AcademyScenario,
    PolicyVariant,
    ScenarioResult,
)


academy = MaestroAcademy()

scenarios = [
    AcademyScenario(
        task_family="SIMPLE_EDIT",
        objective="Fix a typo",
        required_councils={"CM"},
        forbidden_councils={"SC", "FN", "JR"},
        difficulty=1,
    ),
    AcademyScenario(
        task_family="PAYMENT",
        objective="Implement payment webhook",
        required_councils={"PM", "IT", "SC", "FN", "OP", "AY"},
        required_gates={"AY", "OP"},
        difficulty=4,
        risk=5,
    ),
    AcademyScenario(
        task_family="PRIVACY_ANALYTICS",
        objective="Add product analytics",
        required_councils={"PM", "DT", "JR", "IT", "AY"},
        required_gates={"JR", "AY"},
        difficulty=4,
        risk=4,
    ),
    AcademyScenario(
        task_family="ASYNC_RACE",
        objective="Repair a queue race condition",
        required_councils={"IT", "OP", "PR", "AY"},
        required_gates={"AY"},
        difficulty=5,
        risk=4,
    ),
]

baseline = PolicyVariant(
    policy_id="ROUTER-V1",
    version="1",
    description="Over-routes simple tasks and misses PR on async races.",
)

candidate = PolicyVariant(
    policy_id="ROUTER-V2",
    version="2",
    description="Tighter routing with explicit runtime-risk recognition.",
    parent_policy_id="ROUTER-V1",
)

def run(policy, scenario):
    if policy.policy_id == "ROUTER-V1":
        if scenario.task_family == "SIMPLE_EDIT":
            selected = {"CM", "PM", "AY", "SC"}   # over-routing
        elif scenario.task_family == "ASYNC_RACE":
            selected = {"IT", "OP", "AY"}         # misses PR
        else:
            selected = set(scenario.required_councils)
        retries = 2 if scenario.task_family == "ASYNC_RACE" else 0
    else:
        selected = set(scenario.required_councils)
        retries = 0

    return ScenarioResult(
        scenario_id=scenario.scenario_id,
        policy_id=policy.policy_id,
        success=selected.issuperset(scenario.required_councils),
        selected_councils=selected,
        gates_observed=set(scenario.required_gates),
        human_approval_requested=scenario.expected_human_approval,
        retries=retries,
        latency_ms=40 + 10 * len(selected),
        cost_units=1 + 0.1 * len(selected),
        evidence_score=0.95,
    )

baseline_results = [run(baseline, s) for s in scenarios]
assessment = academy.assess(scenarios, baseline_results)

print("BASELINE SCORE:", round(assessment.benchmark.overall_score, 4))
print("WEAKNESSES:")
for w in assessment.benchmark.weaknesses:
    print(" ", w.dimension, w.key, round(w.score, 3), w.severity)

print("CURRICULUM:")
for item in assessment.curriculum:
    print(" ", item.focus, "x", item.repetitions)

replay = academy.compare_policy(baseline, candidate, scenarios, run)
print("REPLAY DELTA:", round(replay.delta, 4))
print("REGRESSIONS:", replay.regressions)

tournament = academy.tournament_policies(
    [baseline, candidate],
    scenarios,
    run,
)
print("TOURNAMENT:")
for standing in tournament.standings:
    print(" ", standing.rank, standing.policy_id, round(standing.mean_score, 4))

print("RECOMMENDED:", tournament.recommended_policy_id)
print("NOTE:", tournament.note)
