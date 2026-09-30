import unittest

from maestro.constitution import ConstitutionViolation
from maestro.enums import CouncilId
from maestro.models import RoutingRequest
from maestro.orchestration.dispatcher import Dispatcher


class RoutingTests(unittest.TestCase):
    def test_only_ex_dispatches(self):
        dispatcher = Dispatcher()
        req = RoutingRequest(
            task_id="TASK-X",
            requested_by=CouncilId.SC,
            targets=[CouncilId.IT],
            action="REMEDIATE",
            reason="Security finding",
        )
        with self.assertRaises(PermissionError):
            dispatcher.dispatch(req, actor=CouncilId.SC)

    def test_routing_request_must_be_via_ex(self):
        dispatcher = Dispatcher()
        req = RoutingRequest(
            task_id="TASK-X",
            requested_by=CouncilId.SC,
            targets=[CouncilId.IT],
            action="REMEDIATE",
            reason="Security finding",
            via=CouncilId.AY,
        )
        with self.assertRaises(ConstitutionViolation):
            dispatcher.dispatch(req, actor=CouncilId.EX)


if __name__ == "__main__":
    unittest.main()
