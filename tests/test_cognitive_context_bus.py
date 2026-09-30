import unittest
from maestro.cognitive_fabric import *
from maestro.sovereign import IntelligenceCapability

class ContextBusTests(unittest.TestCase):
    def test_only_dependencies_are_forwarded(self):
        plan=CognitivePlan("T",[
            CognitiveStage("a",CognitiveRole.PRODUCER,IntelligenceCapability.DIRECT,"X",None,"a"),
            CognitiveStage("b",CognitiveRole.CRITIC,IntelligenceCapability.DIRECT,"X",None,"b",depends_on=("a",)),
        ],context_ref="CTX:1")
        art=[
            StageArtifact("a",CognitiveRole.PRODUCER,"r","p","m","OUT",True),
            StageArtifact("other",CognitiveRole.SCOUT,"r2","p","m","NO",True),
        ]
        env=CognitiveContextBus().compile_for_stage(plan,plan.stages[1],art)
        self.assertEqual(env.context_ref,"CTX:1")
        self.assertEqual(len(env.upstream_artifacts),1)
        self.assertEqual(env.upstream_artifacts[0]["stage_id"],"a")

if __name__=="__main__":
    unittest.main()
