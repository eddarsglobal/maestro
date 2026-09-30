import unittest
from maestro.orchestration.dag import DagEngine,DagNode
from maestro.enums import CouncilId
from maestro.fabric import SkillGraphOptimizer
class T(unittest.TestCase):
 def test_transitive_reduction(self):
  d=DagEngine(); d.add_node(DagNode('a',CouncilId.PM,'A')); d.add_node(DagNode('b',CouncilId.IT,'B',depends_on={'a'})); d.add_node(DagNode('c',CouncilId.SC,'C',depends_on={'a','b'})); o,r=SkillGraphOptimizer().optimize(d); self.assertIn(('c','a'),r.removed_edges); self.assertEqual(o.nodes['c'].depends_on,{'b'})
if __name__=='__main__': unittest.main()
