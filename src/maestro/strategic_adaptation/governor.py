from __future__ import annotations


class StrategyAuthorityViolation(RuntimeError):
    pass


class StrategyAdaptationGovernor:
    """
    Strategy may change method, never objective/authority.
    """

    FORBIDDEN_MUTATIONS = frozenset({
        "mission_objective",
        "constitutional_authority",
        "council_authority",
        "tool_permissions",
        "human_approval",
        "tx_commit_authority",
        "security_constraints",
        "legal_constraints",
    })

    def validate_candidate(self, candidate, claimed_mutations: set[str] | None = None) -> None:
        claimed = claimed_mutations or set()
        forbidden = claimed & set(self.FORBIDDEN_MUTATIONS)
        if forbidden:
            raise StrategyAuthorityViolation(
                "Strategy attempted forbidden mutation: " + ", ".join(sorted(forbidden))
            )
        if not candidate.objective.strip():
            raise StrategyAuthorityViolation("Strategy objective must remain explicit.")

    def validate_transition(self, *, old_objective: str, new_objective: str) -> None:
        if old_objective != new_objective:
            raise StrategyAuthorityViolation(
                "Strategic adaptation may not silently change mission objective."
            )
