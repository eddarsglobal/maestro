from __future__ import annotations

from dataclasses import dataclass

from maestro.academy.replay import ReplayReport
from maestro.academy.tournament import TournamentReport
from .models import AdaptivePolicy, PromotionEvidence
from .policy_manager import AdaptivePolicyManager


@dataclass(slots=True)
class AdaptationProposal:
    policy_id: str
    replay_delta: float
    regressions: int
    academy_recommended: bool
    ready_for_governance: bool
    reason: str


class AdaptiveController:
    """
    Bridge between Academy/Learning and the active policy control plane.
    It prepares governance evidence; it does not bypass activation gates.
    """

    def __init__(self, manager: AdaptivePolicyManager):
        self.manager = manager

    def stage_candidate(self, policy: AdaptivePolicy) -> None:
        self.manager.register(policy)
        self.manager.set_shadow(policy.policy_id)

    def assess(
        self,
        policy: AdaptivePolicy,
        replay: ReplayReport,
        tournament: TournamentReport,
        *,
        shadow_success_rate: float,
    ) -> tuple[AdaptationProposal, PromotionEvidence]:
        recommended = tournament.recommended_policy_id == policy.policy_id
        evidence = PromotionEvidence(
            replay_score=replay.candidate_score,
            baseline_score=replay.baseline_score,
            regression_count=replay.regressions,
            shadow_success_rate=shadow_success_rate,
            evaluation_samples=replay.scenarios,
            academy_recommended=recommended,
        )
        ready = (
            recommended
            and replay.delta > 0
            and replay.regressions == 0
            and shadow_success_rate >= 0.90
        )
        proposal = AdaptationProposal(
            policy_id=policy.policy_id,
            replay_delta=replay.delta,
            regressions=replay.regressions,
            academy_recommended=recommended,
            ready_for_governance=ready,
            reason=(
                "Candidate outperformed baseline without replay regression."
                if ready else
                "Candidate remains in shadow/evaluation."
            ),
        )
        return proposal, evidence
