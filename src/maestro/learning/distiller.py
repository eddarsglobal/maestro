from .models import LearningCandidate,LearningKind
class KnowledgeDistiller:
    def __init__(self,min_support=3): self.min_support=min_support
    def distill(self,failures,successes):
        out=[]
        for k,p in failures.patterns.items():
            if p.support>=self.min_support: out.append(LearningCandidate(LearningKind.FAILURE_PATTERN,f'failure:{k}',f"Repeated verified failure for {p.metadata['task_family']}: {p.metadata['fault']}",list(p.support_experience_ids),list(p.counter_experience_ids)))
        for k,p in successes.patterns.items():
            if p.support>=self.min_support: out.append(LearningCandidate(LearningKind.SUCCESS_PATTERN,f'success:{k}',f"Successful pattern for {p.metadata['task_family']}: councils={p.metadata['councils']} strategies={p.metadata['strategies']}",list(p.support_experience_ids),list(p.counter_experience_ids)))
        return out
