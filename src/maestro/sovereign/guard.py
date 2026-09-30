from __future__ import annotations

class SovereigntyViolation(RuntimeError):
    pass


class SovereigntyGuard:
    """
    Enforces non-negotiable ownership boundaries.
    """

    FORBIDDEN_MODEL_OWNERSHIP = frozenset({
        "mission_lifecycle",
        "constitutional_authority",
        "durable_memory",
        "tool_permissions",
        "council_authority",
        "policy_activation",
        "tx_commit",
        "human_approval",
    })

    def assert_model_contract(self, claimed_ownership: set[str] | frozenset[str]) -> None:
        forbidden = set(claimed_ownership) & set(self.FORBIDDEN_MODEL_OWNERSHIP)
        if forbidden:
            raise SovereigntyViolation(
                "Model/resource attempted to own MAESTRO authority: " + ", ".join(sorted(forbidden))
            )
