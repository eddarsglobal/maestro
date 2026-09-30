import unittest

from maestro.constitution import ConstitutionViolation, authorize_tx_commit, commit_tx_state, register_verdict
from maestro.enums import CouncilId, MissionState, VerdictScope, VerdictValue
from maestro.models import Mission, Verdict


class ConstitutionTests(unittest.TestCase):
    def test_only_ay_can_issue_system_verdict(self):
        mission = Mission("x")
        verdict = Verdict(
            task_id=mission.task_id,
            council=CouncilId.SC,
            value=VerdictValue.JUSTE,
            scope=VerdictScope.SYSTEM,
        )
        with self.assertRaises(ConstitutionViolation):
            register_verdict(mission, verdict)

    def test_ay_must_use_system_scope(self):
        mission = Mission("x")
        verdict = Verdict(
            task_id=mission.task_id,
            council=CouncilId.AY,
            value=VerdictValue.JUSTE,
            scope=VerdictScope.DOMAIN,
        )
        with self.assertRaises(ConstitutionViolation):
            register_verdict(mission, verdict)

    def test_tx_commit_requires_ex_authorization(self):
        mission = Mission("x", state=MissionState.STATE_COMMIT_PENDING)
        mission.system_verdict = Verdict(
            task_id=mission.task_id,
            council=CouncilId.AY,
            value=VerdictValue.JUSTE,
            scope=VerdictScope.SYSTEM,
        )
        with self.assertRaises(ConstitutionViolation):
            commit_tx_state(mission, CouncilId.TX)

    def test_commit_sequence(self):
        mission = Mission("x", state=MissionState.STATE_COMMIT_PENDING)
        register_verdict(
            mission,
            Verdict(
                task_id=mission.task_id,
                council=CouncilId.AY,
                value=VerdictValue.JUSTE,
                scope=VerdictScope.SYSTEM,
            ),
        )
        authorize_tx_commit(mission, CouncilId.EX)
        commit_tx_state(mission, CouncilId.TX)
        self.assertTrue(mission.tx_committed)


if __name__ == "__main__":
    unittest.main()
