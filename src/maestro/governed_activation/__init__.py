from .authority import (
    GovernanceAction,
    GovernanceAttestation,
    GovernanceAuthority,
)
from .engine import GovernedPolicyActivation
from .strict_engine import StrictGovernedPolicyActivation
from .transaction import (
    RuntimeCommitCoordinator,
    RuntimeCommitJournal,
    RuntimeCommitOperation,
    RuntimeCommitRecord,
    RuntimeCommitState,
)
from .ledger import ActivationLedger
from .models import (
    ActivationContract,
    ActivationSnapshot,
    ActivationState,
    CanaryEvidence,
)
from .observation import RuntimeObservationFactory
from .runtime_bridge import AdaptivePolicyRuntimeBridge

GOVERNED_ACTIVATION_LAWS = [
    "APTE-GPA-20 RUNTIME TRANSACTION EVENTS MUST BE CONTENT-ADDRESSED AND HASH-CHAINED",
    "APTE-GPA-19 ONE OGA CANDIDATE MAY OPEN ONLY ONE GPA CONTRACT LINEAGE",
    "APTE-GPA-18 PRODUCTION GENESIS MUST OWN THE DURABLE ADAPTIVE CONTROL PLANE AND RECOVER BEFORE READY",
    "APTE-GPA-17 PRODUCTION MANAGER/GPA COMMITS REQUIRE DURABLE TRANSACTION JOURNAL AND RECOVERY",
    "APTE-GPA-16 ACTIVE ADAPTIVE POLICY STATE MUST SURVIVE PROCESS RESTART",
    "APTE-GPA-15 PRODUCTION AY/EX AUTHORITY REQUIRES CONTRACT-BOUND CHAINED ATTESTATIONS",
    "APTE-GPA-01 PROMOTION EVIDENCE IS NOT ACTIVATION AUTHORITY",
    "APTE-GPA-02 PROMOTION_READY IS REQUIRED BEFORE ACTIVATION PROPOSAL",
    "APTE-GPA-03 AY VALIDATION IS REQUIRED BEFORE EX AUTHORIZATION",
    "APTE-GPA-04 ONLY EX CONTROL-PLANE AUTHORITY MAY AUTHORIZE ACTIVATION",
    "APTE-GPA-05 ACTIVATION CONTRACTS ARE IMMUTABLE",
    "APTE-GPA-06 CANARY PRECEDES ACTIVE",
    "APTE-GPA-07 RUNTIME EVIDENCE IS REQUIRED FOR CANARY VERIFICATION",
    "APTE-GPA-08 ROLLBACK MUST EXIST BEFORE CANARY",
    "APTE-GPA-09 ACTIVATION LIFECYCLE MUST SURVIVE RESTART",
    "APTE-GPA-10 MODELS MAY RECOMMEND BUT MAY NOT AUTHORIZE ACTIVATION",
    "APTE-GPA-11 ADAPTIVE RUNTIME ACTIVATION REQUIRES CANARY_VERIFIED GPA STATE",
    "APTE-GPA-12 RUNTIME ROLLBACK REQUIRES FRESH AY ACKNOWLEDGEMENT AND EX AUTHORIZATION",
    "APTE-GPA-13 PRODUCTION ACTIVATION REQUIRES PERSISTED OGA CANDIDATE PROVENANCE",
    "APTE-GPA-14 ACTIVATION CONTRACT AND CANARY EVIDENCE METADATA ARE DEEPLY IMMUTABLE",
]

__all__ = [
    "GovernanceAction",
    "GovernanceAttestation",
    "GovernanceAuthority",
    "StrictGovernedPolicyActivation",
    "RuntimeCommitCoordinator",
    "RuntimeCommitJournal",
    "RuntimeCommitOperation",
    "RuntimeCommitRecord",
    "RuntimeCommitState",
    "GovernedPolicyActivation",
    "ActivationLedger",
    "ActivationContract",
    "ActivationSnapshot",
    "ActivationState",
    "CanaryEvidence",
    "RuntimeObservationFactory",
    "AdaptivePolicyRuntimeBridge",
    "GOVERNED_ACTIVATION_LAWS",
]
