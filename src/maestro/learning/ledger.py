from .models import LearningStatus
class LearningLedger:
    def __init__(self): self.candidates={}
    def add(self,c):
        if c.candidate_id in self.candidates: raise ValueError('duplicate candidate')
        self.candidates[c.candidate_id]=c
    def approved(self): return [c for c in self.candidates.values() if c.status is LearningStatus.APPROVED]
