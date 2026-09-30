from __future__ import annotations

from dataclasses import replace

from maestro.sovereign.contracts import IntelligenceRequest, IntelligenceResponse
from maestro.intelligence_market import IntelligenceMarket
from .models import CognitiveRunReport, StageArtifact, StageStatus
from .context_bus import CognitiveContextBus
from .budget import CognitiveBudgetGovernor
from .diversity import DiversityPlanner
from .quality import CognitiveQualityGate
from .ledger import CognitiveFabricLedger


class CognitiveFabricExecutor:
    """
    MAESTRO-controlled multi-resource execution.

    No resource can invoke another resource directly.
    """

    def __init__(
        self,
        sovereign_runtime,
        market: IntelligenceMarket,
        *,
        budget: CognitiveBudgetGovernor | None = None,
        diversity: DiversityPlanner | None = None,
        context_bus: CognitiveContextBus | None = None,
        quality: CognitiveQualityGate | None = None,
        ledger: CognitiveFabricLedger | None = None,
        allow_market_exploration: bool = False,
    ):
        self.sovereign = sovereign_runtime
        self.market = market
        self.budget = budget or CognitiveBudgetGovernor()
        self.diversity = diversity or DiversityPlanner()
        self.context_bus = context_bus or CognitiveContextBus()
        self.quality = quality or CognitiveQualityGate()
        self.ledger = ledger or CognitiveFabricLedger()
        self.allow_market_exploration = allow_market_exploration

    def _select_resource(self, stage, used_resources, used_providers):
        eligible = self.sovereign.registry.eligible(stage.capability)
        eligible = self.diversity.filter_candidates(
            eligible,
            already_used_resources=set(used_resources),
            already_used_providers=list(used_providers),
            require_provider_diversity=stage.require_provider_diversity,
        )
        if not eligible:
            raise LookupError(f"No eligible resources for stage {stage.stage_id}")

        # Market may only choose among sovereign-eligible + diversity-filtered resources.
        selection = self.market.selector.select(
            eligible_resource_ids=[d.resource_id for d in eligible],
            task_family=stage.task_family,
            council_id=stage.council_id,
            allow_exploration=self.allow_market_exploration,
        )
        return selection.resource_id

    def execute(self, plan) -> CognitiveRunReport:
        self.budget.validate_plan(plan)
        artifacts = []
        failed = []
        used_resources = []
        used_providers = []

        stage_map = plan.stage_map()

        for stage in plan.stages:
            # All dependencies must have succeeded.
            dependency_failures = [
                dep for dep in stage.depends_on
                if dep in failed or not any(a.stage_id == dep and a.success for a in artifacts)
            ]
            if dependency_failures:
                stage.status = StageStatus.SKIPPED
                failed.append(stage.stage_id)
                continue

            stage.status = StageStatus.RUNNING
            try:
                resource_id = self._select_resource(stage, used_resources, used_providers)
                descriptor = self.sovereign.registry.descriptor(resource_id)
                adapter = self.sovereign.registry.adapter(resource_id)

                envelope = self.context_bus.compile_for_stage(plan, stage, artifacts)

                request = IntelligenceRequest(
                    task_id=plan.task_id,
                    capability=stage.capability,
                    instruction=stage.instruction,
                    context_ref=envelope.context_ref,
                    metadata={
                        "cognitive_role": stage.role.value,
                        "upstream_artifacts": envelope.upstream_artifacts,
                        "stage_id": stage.stage_id,
                        "council_id": stage.council_id,
                    },
                )

                response = adapter.execute(request)
                artifact = StageArtifact(
                    stage_id=stage.stage_id,
                    role=stage.role,
                    resource_id=response.resource_id,
                    provider_id=response.provider_id,
                    model_id=response.model_id,
                    output=response.output,
                    success=response.success,
                    metadata=dict(response.metadata),
                )
                artifact.quality = self.quality.stage_quality(artifact)

                artifacts.append(artifact)
                self.ledger.record_artifact(plan.task_id, artifact)

                used_resources.append(artifact.resource_id)
                used_providers.append(artifact.provider_id)

                stage.status = StageStatus.SUCCEEDED if artifact.success else StageStatus.FAILED
                if not artifact.success:
                    failed.append(stage.stage_id)

            except Exception as exc:
                stage.status = StageStatus.FAILED
                failed.append(stage.stage_id)
                artifact = StageArtifact(
                    stage_id=stage.stage_id,
                    role=stage.role,
                    resource_id="UNAVAILABLE",
                    provider_id="UNAVAILABLE",
                    model_id="UNAVAILABLE",
                    output="",
                    success=False,
                    metadata={"error": str(exc)},
                )
                artifacts.append(artifact)
                self.ledger.record_artifact(plan.task_id, artifact)

        self.budget.validate_output_mass(artifacts)

        return CognitiveRunReport(
            task_id=plan.task_id,
            completed=(len(failed) == 0 and len(artifacts) == len(plan.stages)),
            artifacts=artifacts,
            failed_stage_ids=failed,
            used_resources=used_resources,
            context_ref=plan.context_ref,
        )
