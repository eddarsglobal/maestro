from maestro.councils.registry import COUNCILS
from .capsules import CapsuleStatus
class CouncilInstallDenied(RuntimeError): pass
class DynamicCouncilRegistry:
    def __init__(self,capsules): self.capsules=capsules; self._installed=set()
    @property
    def genesis_ids(self): return {c.value for c in COUNCILS}
    def propose(self,m):
        if m.council_id in self.genesis_ids: raise CouncilInstallDenied('cannot replace Genesis Council')
        m.status=CapsuleStatus.PROPOSED; self.capsules.store(m)
    def promote_to_shadow(self,cid,*,ay_validated:bool):
        if not ay_validated: raise CouncilInstallDenied('AY validation required')
        m=self.capsules.load(cid); m.status=CapsuleStatus.SHADOW; self.capsules.store(m)
    def install(self,cid,*,eval_passed:bool,ay_validated:bool,ex_authorized:bool,human_approved:bool):
        m=self.capsules.load(cid)
        if m.status not in {CapsuleStatus.SHADOW,CapsuleStatus.APPROVED}: raise CouncilInstallDenied('SHADOW required')
        if not all([eval_passed,ay_validated,ex_authorized,human_approved]): raise CouncilInstallDenied('eval + AY + EX + human governance required')
        m.status=CapsuleStatus.INSTALLED; self.capsules.store(m); self._installed.add(cid)
    def installed_dynamic(self): return sorted(self._installed)
