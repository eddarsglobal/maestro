import unittest

from maestro.enums import CouncilId, SideEffectLevel
from maestro.governance.action_firewall import ActionDenied, ActionFirewall, ActionRequest


class ActionFirewallTests(unittest.TestCase):
    def setUp(self):
        self.fw = ActionFirewall()

    def test_read_is_allowed(self):
        self.assertTrue(self.fw.authorize(ActionRequest(CouncilId.RX, "web_search", SideEffectLevel.A0_READ_ONLY)))

    def test_ex_cannot_execute_domain_side_effect(self):
        with self.assertRaises(ActionDenied):
            self.fw.authorize(ActionRequest(CouncilId.EX, "edit_file", SideEffectLevel.A1_REVERSIBLE_LOCAL))

    def test_a4_requires_human(self):
        with self.assertRaises(ActionDenied):
            self.fw.authorize(ActionRequest(CouncilId.IT, "delete_database", SideEffectLevel.A4_IRREVERSIBLE))

        self.assertTrue(
            self.fw.authorize(
                ActionRequest(
                    CouncilId.IT,
                    "delete_database",
                    SideEffectLevel.A4_IRREVERSIBLE,
                    human_approved=True,
                )
            )
        )


if __name__ == "__main__":
    unittest.main()
