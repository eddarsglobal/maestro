from maestro.cognitive_fabric import *
from maestro.intelligence_market import IntelligenceMarket, MarketObservation
from maestro.sovereign import *

class Resource:
    def __init__(self,rid,provider,model):
        self.resource_id=rid; self.provider_id=provider; self.model_id=model
    def execute(self,request):
        upstream=request.metadata.get("upstream_artifacts",[])
        role=request.metadata.get("cognitive_role")
        if role=="SCOUT":
            out="constraints identified"
        elif role=="PRODUCER":
            out="implementation candidate"
        elif role=="CRITIC":
            out=f"critique of {len(upstream)} upstream artifact"
        else:
            out=f"verification over {len(upstream)} upstream artifacts"
        return IntelligenceResponse(self.resource_id,self.provider_id,self.model_id,out,True,{})

reg=IntelligenceResourceRegistry()
profiles=[
    ("tiny-local","ollama","tiny",{IntelligenceCapability.DIRECT,IntelligenceCapability.GENERAL_REASONING}),
    ("coder-local","ollama","coder",{IntelligenceCapability.CODE,IntelligenceCapability.GENERAL_REASONING}),
    ("critic-remote","provider-x","critic",{IntelligenceCapability.CODE,IntelligenceCapability.GENERAL_REASONING}),
]
for rid,p,m,caps in profiles:
    reg.register(ResourceDescriptor(rid,p,m,frozenset(caps),local=(p=="ollama"),quality_score=0.8),Resource(rid,p,m))

rt=SovereignIntelligenceRuntime(reg)
market=IntelligenceMarket(reg)

# Seed market observations.
for _ in range(3):
    market.observe(MarketObservation("tiny-local","CODE_SCOUT","IT",True,0.9,200,0,1,1,True))
    market.observe(MarketObservation("coder-local","CODE","IT",True,0.95,1000,0,1,1,True))
    market.observe(MarketObservation("critic-remote","CODE_REVIEW","IT",True,0.96,1200,0.2,1,1,False))
    market.observe(MarketObservation("tiny-local","VERIFY","IT",True,0.85,300,0,1,1,True))

fabric=CognitiveFabric(rt,market)
plan=fabric.compiler.code_review("TASK-COG-1","Implement secure endpoint",context_ref="MBOS:ctx123")
report=fabric.run(plan)

print("COMPLETED:", report.completed)
print("STAGES:", [(a.stage_id,a.role.value,a.resource_id) for a in report.artifacts])
print("RESOURCES:", report.used_resources)
print("CONTEXT REF:", report.context_ref)
print("FAILED:", report.failed_stage_ids)
