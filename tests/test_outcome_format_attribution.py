import unittest

from maestro.enums import CouncilId, VerdictScope, VerdictValue
from maestro.models import Mission, Verdict
from maestro.outcome_intelligence import (
    AttributionEffect,
    AttributionTarget,
    DimensionResult,
    OutcomeDimension,
    OutcomeIntelligence,
)


class OutcomeFormatAttributionTests(unittest.TestCase):
    def test_format_only_failure_does_not_blame_resource(self):
        mission = Mission("json")
        mission.system_verdict = Verdict(
            task_id=mission.task_id,
            council=CouncilId.AY,
            value=VerdictValue.FAUTE,
            scope=VerdictScope.SYSTEM,
            evidence_ids=["E1"],
        )
        oi = OutcomeIntelligence()
        outcome = oi.capture_from_mission(
            mission,
            task_family="DIRECT_JSON",
            resource_id="ollama::qwen2.5-coder:1.5b",
            dimensions=[
                DimensionResult(OutcomeDimension.SEMANTIC_CORRECTNESS, True, 1.0),
                DimensionResult(OutcomeDimension.FORMAT_COMPLIANCE, False, 0.0),
                DimensionResult(OutcomeDimension.RESOURCE_EXECUTION, True, 1.0),
                DimensionResult(OutcomeDimension.VALIDATOR_INTEGRITY, True, 1.0),
            ],
        )
        resource = outcome.attribution(AttributionTarget.RESOURCE)
        fmt = outcome.attribution(AttributionTarget.FORMAT)
        self.assertEqual(resource.effect, AttributionEffect.INSUFFICIENT)
        self.assertEqual(fmt.effect, AttributionEffect.BLAME)
        directive = oi.market_directive(outcome)
        self.assertFalse(directive.eligible)
        self.assertIsNone(directive.success)

if __name__ == "__main__":
    unittest.main()
