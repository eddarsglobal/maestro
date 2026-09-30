import tempfile
import unittest

from maestro.academy.corpus import AcademyCorpus
from maestro.academy.models import AcademyScenario, ScenarioResult
from maestro.storage.object_store import BinaryObjectStore


class CorpusTests(unittest.TestCase):
    def test_binary_corpus_uses_object_store(self):
        with tempfile.TemporaryDirectory() as td:
            objects = BinaryObjectStore(td)
            corpus = AcademyCorpus(objects)
            scenario = AcademyScenario("X", "x", {"IT"})
            result = ScenarioResult(
                scenario.scenario_id, "P", True, {"IT"}, set(), False
            )
            corpus.put_scenario(scenario)
            corpus.put_result(result)
            self.assertEqual(objects.object_count(), 2)


if __name__ == "__main__":
    unittest.main()
