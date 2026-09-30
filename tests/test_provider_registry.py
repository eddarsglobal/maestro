import unittest

from maestro.autonomous.provider_adapters import ProviderRegistry, ProviderRequest, ProviderResponse


class FakeProvider:
    provider_id = "fake"
    def generate(self, request):
        return ProviderResponse("fake", request.model_id, "ok")


class ProviderRegistryTests(unittest.TestCase):
    def test_provider_adapter(self):
        r = ProviderRegistry()
        r.register(FakeProvider())
        resp = r.generate("fake", ProviderRequest("x", "m1", "do", {}))
        self.assertEqual(resp.output, "ok")


if __name__ == "__main__":
    unittest.main()
