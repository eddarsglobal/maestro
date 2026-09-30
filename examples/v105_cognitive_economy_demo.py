from maestro.cognitive_economy import *

eco=CognitiveEconomy()

low_profile, low_plan=eco.profile_and_plan(
    task_id="TASK-LIGHT",
    risk_score=0.10,
    uncertainty_score=0.10,
    reversibility_score=1.0,
    evidence_demand=0.10,
    time_sensitivity=0.20,
)

critical_profile, critical_plan=eco.profile_and_plan(
    task_id="TASK-CRITICAL",
    risk_score=0.95,
    uncertainty_score=0.90,
    reversibility_score=0.05,
    evidence_demand=1.0,
    time_sensitivity=0.80,
)

decision=eco.utility.decide(
    current_quality=0.91,
    expected_next_quality=0.915,
    current_evidence=0.95,
    expected_next_evidence=0.952,
    added_token_fraction=0.50,
    added_latency_fraction=0.50,
    added_cost_fraction=0.40,
)

print("LIGHT COMPLEXITY:", low_profile.complexity.value)
print("LIGHT TIER:", low_plan.tier.value)
print("LIGHT CALLS:", low_plan.max_resource_calls)
print("CRITICAL COMPLEXITY:", critical_profile.complexity.value)
print("CRITICAL TIER:", critical_plan.tier.value)
print("CRITICAL CRITIC:", critical_plan.require_critic)
print("CRITICAL VERIFIER:", critical_plan.require_verifier)
print("MARGINAL CONTINUE:", decision.continue_spending)
print("MARGINAL REASON:", decision.reason)
