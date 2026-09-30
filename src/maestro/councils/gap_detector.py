from dataclasses import dataclass
from maestro.councils.registry import COUNCILS
from .capsules import CouncilCapsuleManifest
@dataclass(slots=True)
class CapabilityGap:
    required:set[str]; covered:set[str]; missing:set[str]
    @property
    def gap_exists(self): return bool(self.missing)
class CapabilityGapDetector:
    def __init__(self,registry): self.registry=registry
    def available_capabilities(self):
        caps=set()
        for s in COUNCILS.values(): caps.update(x.lower() for x in s.typical_triggers)
        for cid in self.registry.installed_dynamic(): caps.update(x.lower() for x in self.registry.capsules.load(cid).capabilities)
        return caps
    def detect(self,required):
        req={x.lower() for x in required}; avail=self.available_capabilities(); return CapabilityGap(req,req&avail,req-avail)
    def propose_manifest(self,*,council_id,name,authority,missing_capabilities,triggers,cannot_own):
        miss=sorted({x.lower() for x in missing_capabilities})
        if not miss: raise ValueError('no capability gap')
        return CouncilCapsuleManifest(council_id,name,f'$conseil-{council_id.lower()}',authority,miss,list(triggers),list(cannot_own))
