from __future__ import annotations

from dataclasses import dataclass

from maestro.enums import CouncilId


@dataclass(frozen=True, slots=True)
class CouncilSpec:
    council: CouncilId
    system_variable: str
    primary_authority: str
    typical_triggers: tuple[str, ...]
    cannot_own: tuple[str, ...]


COUNCILS: dict[CouncilId, CouncilSpec] = {
    CouncilId.EX: CouncilSpec(
        CouncilId.EX, "$conseil-ex", "routing and active mission lifecycle",
        ("every governed task", "dispatch", "pause/wake/release", "escalation"),
        ("domain execution", "final validation"),
    ),
    CouncilId.AY: CouncilSpec(
        CouncilId.AY, "$conseil-ay", "acceptance contract and system validation",
        ("task contractualization", "audit", "final verdict"),
        ("implementation", "durable state commit"),
    ),
    CouncilId.IT: CouncilSpec(
        CouncilId.IT, "$conseil-it", "software architecture and implementation",
        ("code", "API", "database", "integration", "migration"),
        ("final system verdict",),
    ),
    CouncilId.JR: CouncilSpec(
        CouncilId.JR, "$conseil-jr", "legal and compliance interpretation",
        ("privacy", "contracts", "IP", "consumer regulation"),
        ("tax arithmetic", "security implementation"),
    ),
    CouncilId.MK: CouncilSpec(
        CouncilId.MK, "$conseil-mk", "market and positioning strategy",
        ("market", "pricing strategy", "acquisition", "competition"),
        ("financial viability calculation", "product implementation"),
    ),
    CouncilId.CM: CouncilSpec(
        CouncilId.CM, "$conseil-cm", "external content and media narrative",
        ("landing copy", "campaigns", "SEO content", "media scripts"),
        ("in-product support microcopy", "legal approval"),
    ),
    CouncilId.OP: CouncilSpec(
        CouncilId.OP, "$conseil-op", "operational safety, release, retry watchdog",
        ("release", "rollback", "migration safety", "retry loops"),
        ("final system verdict", "EX routing authority"),
    ),
    CouncilId.FN: CouncilSpec(
        CouncilId.FN, "$conseil-fn", "financial modeling and budget governance",
        ("unit economics", "budget", "provider cost", "margin"),
        ("legal tax interpretation", "product scope"),
    ),
    CouncilId.AD: CouncilSpec(
        CouncilId.AD, "$conseil-ad", "administrative and international operations",
        ("jurisdiction facts", "KYC workflow", "official documents", "international readiness"),
        ("legal interpretation", "tax calculation"),
    ),
    CouncilId.DA: CouncilSpec(
        CouncilId.DA, "$conseil-da", "visual and interaction design",
        ("UI", "UX presentation", "design system", "accessibility presentation"),
        ("product scope", "security architecture"),
    ),
    CouncilId.PM: CouncilSpec(
        CouncilId.PM, "$conseil-pm", "product problem, value and scope",
        ("user problem", "feature scope", "journey", "product criteria"),
        ("final acceptance contract", "implementation"),
    ),
    CouncilId.CS: CouncilSpec(
        CouncilId.CS, "$conseil-cs", "customer success and in-product comprehension",
        ("onboarding", "errors", "empty states", "support friction"),
        ("external marketing content", "product scope"),
    ),
    CouncilId.DT: CouncilSpec(
        CouncilId.DT, "$conseil-dt", "telemetry architecture and measurement truth",
        ("events", "metrics", "funnel instrumentation", "data quality"),
        ("legal basis", "business interpretation alone"),
    ),
    CouncilId.SC: CouncilSpec(
        CouncilId.SC, "$conseil-sc", "security architecture, audit and abuse defense",
        ("auth", "secrets", "threats", "security testing", "abuse"),
        ("overall product validation", "legal interpretation"),
    ),
    CouncilId.TX: CouncilSpec(
        CouncilId.TX, "$conseil-tx", "durable traceability and project state",
        ("ADR", "state commit", "documentation", "decision lineage"),
        ("active routing", "private chain-of-thought"),
    ),
    CouncilId.PR: CouncilSpec(
        CouncilId.PR, "$conseil-pr", "performance, capacity and runtime reality",
        ("latency", "load", "capacity", "resource usage"),
        ("final business verdict", "implementation"),
    ),
    CouncilId.AI: CouncilSpec(
        CouncilId.AI, "$conseil-ai", "product AI architecture and evaluation",
        ("LLM feature", "RAG", "model evaluation", "AI guardrails"),
        ("APTE internal orchestration", "application code implementation"),
    ),
    CouncilId.RX: CouncilSpec(
        CouncilId.RX, "$conseil-rx", "external research and breakout intelligence",
        ("dead-end", "fresh external evidence", "provider contradiction"),
        ("production implementation", "direct worker wake/release"),
    ),
}


def get_council(council: CouncilId) -> CouncilSpec:
    return COUNCILS[council]


def validate_registry() -> None:
    expected = set(CouncilId)
    actual = set(COUNCILS)
    if actual != expected:
        missing = sorted(x.value for x in expected - actual)
        extra = sorted(x.value for x in actual - expected)
        raise ValueError(f"Council registry mismatch; missing={missing}, extra={extra}")

    variables = [spec.system_variable for spec in COUNCILS.values()]
    if len(variables) != len(set(variables)):
        raise ValueError("Council system variables must be unique.")
