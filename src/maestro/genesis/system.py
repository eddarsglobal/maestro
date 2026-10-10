from __future__ import annotations

from pathlib import Path
from maestro.sovereign import IntelligenceCapability

from maestro.os.operating_system import MaestroOperatingSystem
from maestro.genesis.boot import BootValidator
from maestro.genesis.health import HealthInspector
from maestro.sovereign import SovereignIntelligenceRuntime
from maestro.intelligence_market import IntelligenceMarket
from maestro.cognitive_fabric import CognitiveFabric
from maestro.cognitive_economy import CognitiveEconomy
from maestro.meta_cognition import MetaCognition
from maestro.strategic_adaptation import StrategicAdaptationEngine
from maestro.outcome_intelligence import OutcomeIntelligence
from maestro.outcome_governed_adaptation import OutcomeGovernedAdaptation
from maestro.adaptive import AdaptiveController, PersistentAdaptivePolicyManager
from maestro.governed_activation import GovernedPolicyActivation, StrictGovernedPolicyActivation


class ProductionGenesisSystem:
    """
    v1.0 production composition root.

    This is the public system boundary for deploying MAESTRO as one coherent
    runtime instead of importing internal subsystems individually.
    """

    VERSION = "1.1.0"

    def __init__(self, runtime_dir: str | Path):
        self.runtime_dir = Path(runtime_dir)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

        self.boot = BootValidator()
        self.health = HealthInspector()
        self.os = MaestroOperatingSystem(self.runtime_dir / "os")
        # Platform-specific intelligence is not part of sovereign
        # Genesis identity. Explicit external composition may bind
        # a compatibility edge later; zero-platform boot remains
        # sovereign and valid.
        self.local_intelligence = None
        self.sovereign_intelligence = SovereignIntelligenceRuntime()
        self.intelligence_market = IntelligenceMarket(self.sovereign_intelligence.registry)
        self.cognitive_fabric = CognitiveFabric(self.sovereign_intelligence, self.intelligence_market)
        self.cognitive_economy = CognitiveEconomy()
        self.meta_cognition = MetaCognition()
        self.strategic_adaptation = StrategicAdaptationEngine()
        self.adaptive_policy_manager = PersistentAdaptivePolicyManager(
            self.runtime_dir / "adaptive" / "control_plane.json"
        )
        self.adaptive_controller = AdaptiveController(
            self.adaptive_policy_manager
        )
        self.outcome_intelligence = OutcomeIntelligence(self.runtime_dir / "outcome_intelligence" / "outcomes.jsonl")
        self.outcome_governed_adaptation = OutcomeGovernedAdaptation(self.runtime_dir / "outcome_governed_adaptation" / "candidates.jsonl")
        self.governed_activation = StrictGovernedPolicyActivation(
            Path(runtime_dir) / "governed_activation" / "activation.jsonl",
            candidate_ledger=self.outcome_governed_adaptation.ledger,
        )

    def start(self) -> dict:
        boot = self.boot.validate()

        recovered = (
            self.governed_activation
            .recover_runtime_transactions(
                self.adaptive_policy_manager
            )
        )

        blocked = (
            self.governed_activation
            .runtime_commit_journal
            .blocked()
        )

        if blocked:
            ids = ", ".join(
                row.transaction_id
                for row in blocked
            )
            raise RuntimeError(
                "Production boot blocked by unresolved runtime "
                f"transaction conflict(s): {ids}"
            )

        summary = {
            "processed": len(recovered),
            "committed": sum(
                1
                for row in recovered
                if row.state.value == "GPA_COMMITTED"
            ),
            "aborted": sum(
                1
                for row in recovered
                if row.state.value == "ABORTED"
            ),
            "blocked": 0,
        }

        intelligence_registry = self.sovereign_intelligence.registry
        intelligence_resources = intelligence_registry.all()
        degraded_state = self.sovereign_intelligence.degraded.assess(
            intelligence_registry
        )

        available_capability_set = set(
            degraded_state.available_capabilities
        )
        available_capabilities = sorted(
            available_capability_set
        )
        known_capabilities = sorted(
            capability.value
            for capability in IntelligenceCapability
        )
        unavailable_capabilities = [
            capability
            for capability in known_capabilities
            if capability not in available_capability_set
        ]

        available_resources = sum(
            1
            for resource in intelligence_resources
            if resource.status.value != "UNAVAILABLE"
        )

        intelligence_state = (
            "SOVEREIGN_DEGRADED"
            if available_resources == 0
            else degraded_state.level.value
        )

        return {
            "version": self.VERSION,
            "status": "READY",
            "boot": boot,
            "runtime_recovery": summary,
            "intelligence": {
                "state": intelligence_state,
                "level": degraded_state.level.value,
                "available_resources": available_resources,
                "registered_resources": len(intelligence_resources),
                "available_capabilities": available_capabilities,
                "unavailable_capabilities": unavailable_capabilities,
                "reason": degraded_state.reason,
            },
        }
    def health_report(self):
        return self.health.inspect(runtime_dir=self.runtime_dir)
