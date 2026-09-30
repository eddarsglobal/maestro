import unittest

from maestro.adaptive.skills import SkillCandidate
from maestro.os.skill_dag import SkillDagCompiler


class SkillDagTests(unittest.TestCase):
    def test_skill_compiles_to_sequence(self):
        skill = SkillCandidate(
            "PAYMENT_SKILL", "PAYMENT",
            ["PM", "IT", "SC"],
            ["DEFINE", "IMPLEMENT", "AUDIT"],
            ["tool"], ["E1", "E2", "E3"],
        )
        dag = SkillDagCompiler().compile(skill)
        order = dag.topological_order()
        self.assertEqual(len(order), 3)
        self.assertEqual(dag.nodes[order[0]].council.value, "PM")
        self.assertEqual(dag.nodes[order[-1]].council.value, "SC")


if __name__ == "__main__":
    unittest.main()
