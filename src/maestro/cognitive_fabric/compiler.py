from __future__ import annotations

from maestro.sovereign.contracts import IntelligenceCapability
from .models import CognitivePlan, CognitiveRole, CognitiveStage


class CognitivePlanCompiler:
    """
    Compiles bounded cognitive workflows.

    This is not free-form model chat. MAESTRO owns the plan and every stage.
    """

    def direct(self, task_id: str, instruction: str, *, council_id: str | None = None, context_ref: str | None = None) -> CognitivePlan:
        return CognitivePlan(
            task_id=task_id,
            context_ref=context_ref,
            stages=[
                CognitiveStage(
                    "produce",
                    CognitiveRole.PRODUCER,
                    IntelligenceCapability.DIRECT,
                    "DIRECT",
                    council_id,
                    instruction,
                )
            ],
        )

    def reason_and_critique(
        self,
        task_id: str,
        instruction: str,
        *,
        council_id: str | None = None,
        context_ref: str | None = None,
    ) -> CognitivePlan:
        return CognitivePlan(
            task_id=task_id,
            context_ref=context_ref,
            stages=[
                CognitiveStage(
                    "produce",
                    CognitiveRole.PRODUCER,
                    IntelligenceCapability.GENERAL_REASONING,
                    "GENERAL_REASONING",
                    council_id,
                    instruction,
                ),
                CognitiveStage(
                    "critique",
                    CognitiveRole.CRITIC,
                    IntelligenceCapability.GENERAL_REASONING,
                    "CRITIQUE",
                    council_id,
                    "Critique the producer result for unsupported claims, omissions, and contradictions.",
                    depends_on=("produce",),
                    require_provider_diversity=True,
                ),
            ],
        )

    def code_review(
        self,
        task_id: str,
        instruction: str,
        *,
        council_id: str = "IT",
        context_ref: str | None = None,
    ) -> CognitivePlan:
        return CognitivePlan(
            task_id=task_id,
            context_ref=context_ref,
            stages=[
                CognitiveStage(
                    "scout",
                    CognitiveRole.SCOUT,
                    IntelligenceCapability.DIRECT,
                    "CODE_SCOUT",
                    council_id,
                    "Identify the minimal implementation risks and relevant constraints.",
                ),
                CognitiveStage(
                    "produce",
                    CognitiveRole.PRODUCER,
                    IntelligenceCapability.CODE,
                    "CODE",
                    council_id,
                    instruction,
                    depends_on=("scout",),
                ),
                CognitiveStage(
                    "critic",
                    CognitiveRole.CRITIC,
                    IntelligenceCapability.CODE,
                    "CODE_REVIEW",
                    council_id,
                    "Review the produced code/result for defects and regressions.",
                    depends_on=("produce",),
                    require_provider_diversity=True,
                ),
                CognitiveStage(
                    "verify",
                    CognitiveRole.VERIFIER,
                    IntelligenceCapability.GENERAL_REASONING,
                    "VERIFY",
                    council_id,
                    "Verify whether the result and critique satisfy the stated objective and evidence.",
                    depends_on=("produce", "critic"),
                ),
            ],
        )
