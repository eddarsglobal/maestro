from maestro.sovereign import *

class Resource:
    def __init__(self, rid, provider, model, fail=False):
        self.resource_id=rid
        self.provider_id=provider
        self.model_id=model
        self.fail=fail
    def execute(self, request):
        if self.fail:
            raise RuntimeError("simulated provider failure")
        return IntelligenceResponse(
            self.resource_id, self.provider_id, self.model_id,
            f"{self.model_id}: OK", True, {}
        )

reg = IntelligenceResourceRegistry()
reg.register(
    ResourceDescriptor(
        "local-small","ollama","tiny",
        frozenset({IntelligenceCapability.DIRECT}),
        local=True, quality_score=0.8
    ),
    Resource("local-small","ollama","tiny",fail=True)
)
reg.register(
    ResourceDescriptor(
        "remote-backup","provider-x","model-y",
        frozenset({IntelligenceCapability.DIRECT}),
        local=False, quality_score=0.9
    ),
    Resource("remote-backup","provider-x","model-y")
)

runtime = SovereignIntelligenceRuntime(reg)
req = IntelligenceRequest("TASK-1", IntelligenceCapability.DIRECT, "ping")
out = runtime.execute(req)

print("SELECTED AFTER FALLBACK:", out.resource_id)
print("OUTPUT:", out.output)
print("FALLBACK FROM:", out.metadata.get("fallback_from"))

reg.set_status("local-small", ResourceStatus.UNAVAILABLE)
reg.set_status("remote-backup", ResourceStatus.UNAVAILABLE)
state = runtime.degraded.assess(reg)
print("NO MODEL MODE:", state.level.value)

guard = SovereigntyGuard()
try:
    guard.assert_model_contract({"tx_commit"})
except SovereigntyViolation:
    print("MODEL AUTHORITY BLOCKED: True")
