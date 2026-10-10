"""MAESTRO — APTE Production Genesis."""

from .models import Mission, Verdict, RoutingRequest, Evidence
from .runtime.kernel import MaestroKernel
from .orchestration.dag import DagEngine, DagNode
from .orchestration.retry_ledger import RetryLedger, RetryAttempt
from .runtime.context_compiler import ContextCompiler, CouncilContext
from .runtime.checkpoint import CheckpointStore
from .tools.registry import ToolRegistry, ToolSpec
from .learning.models import ExperienceRecord, LearningCandidate
from .learning.engine import LearningEngine
from .councils.dynamic_registry import DynamicCouncilRegistry
from .councils.capsules import CouncilCapsuleManifest
from .governance.mass_budget import LightnessGovernor, MassBudget
from .academy import MaestroAcademy, AcademyScenario, ScenarioResult, PolicyVariant
from .adaptive import (
    AdaptivePolicy, PolicyKind, PolicyStatus, PromotionEvidence,
    AdaptivePolicyManager, AdaptiveRoutingEngine, AdaptiveContextPolicy,
    ToolPolicyLearner, ModelPolicyLearner, RetryStrategyLearner,
    SkillFactory, ArchetypeDiscovery, AdaptiveController,
)
from .autonomous import *
from .os import *
from .genesis import *

__version__ = "1.1.0"

# LocalIntelligence is a platform-specific compatibility edge.
# Keep its public import available lazily without making Ollama
# part of MAESTRO core package initialization.
def __getattr__(name: str):
    if name == "LocalIntelligence":
        from .local_intelligence import LocalIntelligence
        return LocalIntelligence

    raise AttributeError(
        f"module {__name__!r} has no attribute {name!r}"
    )



from .sovereign import *

from .intelligence_market import *

from .cognitive_fabric import *

from .cognitive_economy import *

from .meta_cognition import *

from .strategic_adaptation import *

from .outcome_intelligence import *

from .outcome_governed_adaptation import *

from .governed_activation import GovernedPolicyActivation
