from __future__ import annotations

from dataclasses import dataclass

from maestro.enums import CouncilId, SideEffectLevel


@dataclass(frozen=True, slots=True)
class ActionRequest:
    actor: CouncilId
    action: str
    level: SideEffectLevel
    human_approved: bool = False
    policy_approved: bool = False


class ActionDenied(PermissionError):
    pass


class ActionFirewall:
    """
    Minimal constitutional action firewall.

    v0.1 rules:
    - A0: allowed.
    - A1: allowed for domain executors; EX/AY/TX remain constrained by role.
    - A2: requires policy approval.
    - A3: requires policy approval + human approval.
    - A4: requires human approval, and EX/AY are never direct executors.
    """

    non_execution_councils = {CouncilId.EX, CouncilId.AY}

    def authorize(self, request: ActionRequest) -> bool:
        if request.level is SideEffectLevel.A0_READ_ONLY:
            return True

        if request.actor in self.non_execution_councils:
            raise ActionDenied(f"{request.actor.value} is not a domain execution Council.")

        if request.level is SideEffectLevel.A1_REVERSIBLE_LOCAL:
            return True

        if request.level is SideEffectLevel.A2_REVERSIBLE_EXTERNAL:
            if not request.policy_approved:
                raise ActionDenied("A2 action requires policy approval.")
            return True

        if request.level is SideEffectLevel.A3_MATERIAL_EXTERNAL:
            if not (request.policy_approved and request.human_approved):
                raise ActionDenied("A3 action requires policy and human approval.")
            return True

        if request.level is SideEffectLevel.A4_IRREVERSIBLE:
            if not request.human_approved:
                raise ActionDenied("A4 irreversible action requires human approval.")
            return True

        raise ActionDenied("Unknown action level.")
