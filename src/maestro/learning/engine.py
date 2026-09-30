from .atlas import FailureAtlas,SuccessAtlas
from .distiller import KnowledgeDistiller
from .ledger import LearningLedger
class LearningEngine:
    def __init__(self,experiences): self.experiences=experiences; self.failures=FailureAtlas(); self.successes=SuccessAtlas(); self.distiller=KnowledgeDistiller(); self.ledger=LearningLedger()
    def ingest(self,e):
        eid=self.experiences.add(e)
        if e.verified: self.failures.observe(e); self.successes.observe(e)
        return eid
    def distill_candidates(self):
        existing={c.key for c in self.ledger.candidates.values()}; ids=[]
        for c in self.distiller.distill(self.failures,self.successes):
            if c.key not in existing: self.ledger.add(c); existing.add(c.key); ids.append(c.candidate_id)
        return ids
