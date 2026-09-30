from maestro.academy import MaestroAcademy, AcademyScenario, PolicyVariant, ScenarioResult
from maestro.adaptive import (
    AdaptiveController,
    AdaptivePolicy,
    AdaptivePolicyManager,
    AdaptiveRoutingEngine,
    PolicyKind,
)


academy = MaestroAcademy()
manager = AdaptivePolicyManager()
controller = AdaptiveController(manager)
routing = AdaptiveRoutingEngine()

genesis = AdaptivePolicy(
    kind=PolicyKind.ROUTING,
    version=1,
    description="Genesis routing policy",
    parameters={
        "rules": {
            "SIMPLE_EDIT": ["CM", "PM", "AY", "SC"],
            "ASYNC_RACE": ["IT", "OP", "AY"],
        },
        "default": ["AY"],
    },
)
manager.bootstrap_active(genesis)

candidate = AdaptivePolicy(
    kind=PolicyKind.ROUTING,
    version=2,
    parent_policy_id=genesis.policy_id,
    description="Academy-learned routing candidate",
    parameters={
        "rules": {
            "SIMPLE_EDIT": ["CM"],
            "ASYNC_RACE": ["IT", "OP", "PR", "AY"],
        },
        "default": ["AY"],
    },
)
controller.stage_candidate(candidate)

scenarios = [
    AcademyScenario(
        task_family="SIMPLE_EDIT",
        objective="Fix copy",
        required_councils={"CM"},
        forbidden_councils={"SC", "FN", "JR"},
    ),
    AcademyScenario(
        task_family="ASYNC_RACE",
        objective="Fix queue race",
        required_councils={"IT", "OP", "PR", "AY"},
        required_gates={"AY"},
    ),
]

base_view = PolicyVariant(genesis.policy_id, "1", "genesis")
cand_view = PolicyVariant(candidate.policy_id, "2", "candidate")

def run(policy_view, scenario):
    actual = genesis if policy_view.policy_id == genesis.policy_id else candidate
    decision = routing.route(actual, task_family=scenario.task_family)
    selected = decision.councils
    return ScenarioResult(
        scenario_id=scenario.scenario_id,
        policy_id=policy_view.policy_id,
        success=selected.issuperset(scenario.required_councils),
        selected_councils=selected,
        gates_observed=set(scenario.required_gates),
        human_approval_requested=False,
        retries=0 if scenario.required_councils.issubset(selected) else 2,
        latency_ms=10 * len(selected),
        cost_units=float(len(selected)),
        evidence_score=0.95,
    )

replay = academy.compare_policy(base_view, cand_view, scenarios, run)
tournament = academy.tournament_policies([base_view, cand_view], scenarios, run)

proposal, evidence = controller.assess(
    candidate,
    replay,
    tournament,
    shadow_success_rate=0.98,
)

print("ACTIVE BEFORE:", manager.active(PolicyKind.ROUTING).version)
print("CANDIDATE READY:", proposal.ready_for_governance)
print("REPLAY DELTA:", round(proposal.replay_delta, 4))
print("REGRESSIONS:", proposal.regressions)

manager.activate(
    candidate.policy_id,
    evidence=evidence,
    ay_validated=True,
    ex_authorized=True,
    min_samples=2,
)

print("ACTIVE AFTER:", manager.active(PolicyKind.ROUTING).version)

# Native rollback demonstration.
manager.rollback(
    PolicyKind.ROUTING,
    ex_authorized=True,
    ay_acknowledged=True,
    reason="demo rollback",
)

print("ACTIVE AFTER ROLLBACK:", manager.active(PolicyKind.ROUTING).version)
