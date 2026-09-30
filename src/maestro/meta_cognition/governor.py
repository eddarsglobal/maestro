from __future__ import annotations

from .models import MetaAction, MetaSignalType


class MetaCognitionGovernor:
    """
    Enforces that meta-cognition can recommend bounded actions but cannot grant authority.
    """

    FORBIDDEN_AUTONOMOUS_ACTIONS = frozenset({
        "WAIVE_SECURITY",
        "WAIVE_LEGAL",
        "GRANT_TOOL_PERMISSION",
        "AUTHORIZE_TX_COMMIT",
        "SELF_MODIFY_CONSTITUTION",
        "APPROVE_IRREVERSIBLE_ACTION",
    })

    def validate_recommendations(self, assessment) -> None:
        for action in assessment.recommended_actions:
            if action.value in self.FORBIDDEN_AUTONOMOUS_ACTIONS:
                raise RuntimeError(f"Meta-cognition attempted forbidden authority: {action.value}")

    def requires_hard_stop(self, assessment) -> bool:
        return (
            MetaAction.BLOCK in assessment.recommended_actions
            or MetaSignalType.HUMAN_AUTHORIZATION_REQUIRED
            in {s.signal_type for s in assessment.signals}
        )
