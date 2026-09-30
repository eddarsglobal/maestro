from dataclasses import dataclass
from .models import LearningStatus
class PromotionDenied(RuntimeError): pass
@dataclass(frozen=True,slots=True)
class EvaluationResult: replay_score:float; regression_count:int; shadow_success_rate:float; samples:int
class PromotionGate:
    def __init__(self,min_support=3,min_samples=10,min_replay_score=.90,max_regressions=0,min_shadow_success_rate=.90): self.min_support=min_support; self.min_samples=min_samples; self.min_replay_score=min_replay_score; self.max_regressions=max_regressions; self.min_shadow_success_rate=min_shadow_success_rate
    def evaluate(self,c,result,*,ay_validated:bool,ex_authorized:bool):
        if c.support_count<self.min_support: raise PromotionDenied('insufficient support')
        if result.samples<self.min_samples: raise PromotionDenied('insufficient samples')
        if result.replay_score<self.min_replay_score or result.regression_count>self.max_regressions or result.shadow_success_rate<self.min_shadow_success_rate: raise PromotionDenied('evaluation failed')
        if not ay_validated: raise PromotionDenied('AY validation required')
        if not ex_authorized: raise PromotionDenied('EX authorization required')
        c.evaluation_score=result.replay_score; c.status=LearningStatus.APPROVED; return True
