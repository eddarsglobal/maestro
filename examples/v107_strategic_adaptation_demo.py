from maestro.strategic_adaptation import *

engine=StrategicAdaptationEngine()

current=StrategyCandidate(
    strategy_id="TASK-1:current",
    family="CODE_FIX",
    objective="repair failing build without changing requirements",
    method="RETRY_SAME_APPROACH",
    expected_quality=.4,
    expected_evidence_gain=.2,
    expected_cost=.6,
    expected_latency=.6,
)

selected, evaluations, decision=engine.propose_and_select(
    task_id="TASK-1",
    objective=current.objective,
    family=current.family,
    current_strategy_id=current.strategy_id,
    current_method=current.method,
    trigger=StrategyTrigger.RETRY_LOOP,
    available_capabilities={"MULTI_RESOURCE"},
    risk_score=.7,
    evidence_urgency=.9,
    cost_pressure=.5,
    latency_pressure=.5,
)

transition=engine.authorize_transition(
    task_id="TASK-1",
    current_strategy=current,
    selected_strategy=selected,
    trigger=StrategyTrigger.RETRY_LOOP,
    authorized=True,
)

rollback=engine.rollback.should_rollback(
    baseline_quality=.55,
    new_quality=.85,
    baseline_evidence=.40,
    new_evidence=.90,
    baseline_cost=.50,
    new_cost=.60,
)

print("CURRENT:", current.method)
print("SELECTED:", selected.method)
print("SELECTED ID:", selected.strategy_id)
print("SWITCH:", decision.switch_required)
print("AUTHORIZED:", transition.authorized)
print("OBJECTIVE PRESERVED:", current.objective == selected.objective)
print("ROLLBACK REQUIRED:", rollback)
