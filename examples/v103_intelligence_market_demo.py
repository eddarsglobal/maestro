from maestro.intelligence_market import *
from maestro.sovereign import *

class R:
    def __init__(self,rid): self.resource_id=rid; self.provider_id="p"; self.model_id=rid
    def execute(self,request): return IntelligenceResponse(self.resource_id,"p",self.model_id,"OK",True)

reg=IntelligenceResourceRegistry()
for rid in ["local-small","local-code","remote-heavy"]:
    caps={IntelligenceCapability.DIRECT,IntelligenceCapability.GENERAL_REASONING}
    if "code" in rid:
        caps.add(IntelligenceCapability.CODE)
    reg.register(ResourceDescriptor(rid,"p",rid,frozenset(caps),local=rid.startswith("local")),R(rid))

market=IntelligenceMarket(reg)

# Three observations each so selection can exploit rather than explore.
for _ in range(3):
    market.observe(MarketObservation("local-small","DIRECT","EX",True,0.82,900,0.0,1,1,True))
    market.observe(MarketObservation("remote-heavy","DIRECT","EX",True,0.96,2200,0.3,1,1,False))
    market.observe(MarketObservation("local-code","CODE","IT",True,0.97,1200,0.0,1,1,True))

direct=market.choose(
    capability=IntelligenceCapability.DIRECT,
    task_family="DIRECT",
    council_id="EX",
    allow_exploration=False,
)
code=market.choose(
    capability=IntelligenceCapability.CODE,
    task_family="CODE",
    council_id="IT",
    allow_exploration=False,
)

print("EX/DIRECT WINNER:", direct.resource_id, round(direct.market_score,4))
print("IT/CODE WINNER:", code.resource_id, round(code.market_score,4))

# Show bounded exploration with an under-tested new resource.
reg.register(
    ResourceDescriptor(
        "new-model","p","new-model",
        frozenset({IntelligenceCapability.DIRECT}),
        local=True
    ),
    R("new-model")
)
explore=market.choose(
    capability=IntelligenceCapability.DIRECT,
    task_family="DIRECT",
    council_id="EX",
    allow_exploration=True,
)
print("EXPLORATION:", explore.resource_id, explore.explored)
