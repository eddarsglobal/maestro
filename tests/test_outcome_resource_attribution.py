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


class OutcomeResourceAttributionTests(unittest.TestCase):
    def test_resource_execution_failure_can_create_negative_market_directive(self):
        mission = Mission("resource failure")
        mission.system_verdict = Verdict(
            task_id=mission.task_id,
            council=CouncilId.AY,
            value=VerdictValue.FAUTE,
            scope=VerdictScope.SYSTEM,
        )
        oi = OutcomeIntelligence()
        outcome = oi.capture_from_mission(
            mission,
            task_family="DIRECT",
            resource_id="r1",
            dimensions=[
                DimensionResult(OutcomeDimension.RESOURCE_EXECUTION, False, 0.0),
                DimensionResult(OutcomeDimension.VALIDATOR_INTEGRITY, True, 1.0),
            ],
        )
        finding = outcome.attribution(AttributionTarget.RESOURCE)
        self.assertEqual(finding.effect, AttributionEffect.BLAME)
        directive = oi.market_directive(outcome)
        self.assertTrue(directive.eligible)
        self.assertFalse(directive.success)
        self.assertGreaterEqual(directive.confidence, 0.70)

if __name__ == "__main__":
    unittest.main()
