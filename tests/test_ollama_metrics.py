import unittest
from maestro.providers.ollama.metrics import OllamaMetricsRecorder
from maestro.providers.ollama.models import OllamaGenerationResult

class OllamaMetricsTests(unittest.TestCase):
    def test_summary(self):
        r = OllamaMetricsRecorder()
        for ms, tps in [(1000, 50),(2000, 100)]:
            # eval_count/eval_duration are chosen to produce tps.
            result = OllamaGenerationResult("m","ok",True,"stop",int(ms*1e6),0,1,int(tps),1_000_000_000)
            r.record_generation(task_class="DIRECT", result=result)
        s = r.summarize("m","DIRECT")
        self.assertEqual(s["samples"],2)
        self.assertAlmostEqual(s["mean_latency_ms"],1500.0)
        self.assertAlmostEqual(s["mean_tokens_per_second"],75.0)

if __name__ == "__main__":
    unittest.main()
