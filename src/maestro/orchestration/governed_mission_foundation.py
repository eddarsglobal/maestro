from __future__ import annotations

import hashlib
import itertools
import json

from dataclasses import dataclass, field
from typing import Any, Iterable

from maestro.councils.registry import COUNCILS


GOVERNED_MISSION_FOUNDATION_VERSION = 1


class MissionFoundationInvariantError(
    ValueError
):
    pass


class MissionAnalysisIncompleteError(
    MissionFoundationInvariantError
):
    pass


class CouncilGraphIncompleteError(
    MissionFoundationInvariantError
):
    pass


def _required_text(
    value: str,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string."
        )

    value = value.strip()

    if not value:
        raise MissionFoundationInvariantError(
            f"{name} must not be empty."
        )

    if "\x00" in value:
        raise MissionFoundationInvariantError(
            f"{name} must not contain NUL."
        )

    return value


def _normalized_tuple(
    values: Iterable[str],
    name: str,
    *,
    require_nonempty: bool = True,
) -> tuple[str, ...]:
    rows = tuple(
        sorted(
            _required_text(
                value,
                name,
            )
            for value in values
        )
    )

    if require_nonempty and not rows:
        raise MissionFoundationInvariantError(
            f"{name} must not be empty."
        )

    if len(rows) != len(set(rows)):
        raise MissionFoundationInvariantError(
            f"{name} values must be unique."
        )

    return rows


def _stable_id(
    prefix: str,
    payload: dict[str, Any],
) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )

    digest = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()

    return (
        prefix
        + "-"
        + digest[:24]
    )


@dataclass(
    frozen=True,
    slots=True,
)
class MissionContract:
    objective: str
    scope: str
    requested_output: str

    constraints: tuple[
        str,
        ...,
    ]

    acceptance_criteria: tuple[
        str,
        ...,
    ]

    authority_requirements: tuple[
        str,
        ...,
    ]

    evidence_obligations: tuple[
        str,
        ...,
    ]

    contract_id: str = field(
        init=False
    )

    def __post_init__(
        self,
    ) -> None:
        for name in (
            "objective",
            "scope",
            "requested_output",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(
                        self,
                        name,
                    ),
                    name,
                ),
            )

        for name in (
            "constraints",
            "acceptance_criteria",
            "authority_requirements",
            "evidence_obligations",
        ):
            object.__setattr__(
                self,
                name,
                _normalized_tuple(
                    getattr(
                        self,
                        name,
                    ),
                    name,
                ),
            )

        object.__setattr__(
            self,
            "contract_id",
            _stable_id(
                "MC",
                {
                    "version": (
                        GOVERNED_MISSION_FOUNDATION_VERSION
                    ),
                    "objective": self.objective,
                    "scope": self.scope,
                    "requested_output": (
                        self.requested_output
                    ),
                    "constraints": list(
                        self.constraints
                    ),
                    "acceptance_criteria": list(
                        self.acceptance_criteria
                    ),
                    "authority_requirements": list(
                        self.authority_requirements
                    ),
                    "evidence_obligations": list(
                        self.evidence_obligations
                    ),
                },
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_MISSION_FOUNDATION_VERSION
            ),
            "contract_id": self.contract_id,
            "objective": self.objective,
            "scope": self.scope,
            "requested_output": (
                self.requested_output
            ),
            "constraints": list(
                self.constraints
            ),
            "acceptance_criteria": list(
                self.acceptance_criteria
            ),
            "authority_requirements": list(
                self.authority_requirements
            ),
            "evidence_obligations": list(
                self.evidence_obligations
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class CapabilityRule:
    rule_id: str
    capability_id: str
    keywords: tuple[
        str,
        ...,
    ]
    rationale: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "rule_id",
            _required_text(
                self.rule_id,
                "rule_id",
            ),
        )

        object.__setattr__(
            self,
            "capability_id",
            _required_text(
                self.capability_id,
                "capability_id",
            ),
        )

        object.__setattr__(
            self,
            "rationale",
            _required_text(
                self.rationale,
                "rationale",
            ),
        )

        keywords = tuple(
            sorted(
                {
                    _required_text(
                        value,
                        "keyword",
                    ).casefold()
                    for value
                    in self.keywords
                }
            )
        )

        if not keywords:
            raise MissionFoundationInvariantError(
                "CapabilityRule requires "
                "at least one keyword."
            )

        object.__setattr__(
            self,
            "keywords",
            keywords,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CapabilityDemand:
    capability_id: str
    matched_rule_ids: tuple[
        str,
        ...,
    ]
    rationales: tuple[
        str,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "capability_id",
            _required_text(
                self.capability_id,
                "capability_id",
            ),
        )

        object.__setattr__(
            self,
            "matched_rule_ids",
            _normalized_tuple(
                self.matched_rule_ids,
                "matched_rule_id",
            ),
        )

        object.__setattr__(
            self,
            "rationales",
            _normalized_tuple(
                self.rationales,
                "rationale",
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "capability_id": (
                self.capability_id
            ),
            "matched_rule_ids": list(
                self.matched_rule_ids
            ),
            "rationales": list(
                self.rationales
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class MissionCapabilityDemand:
    contract_id: str
    demands: tuple[
        CapabilityDemand,
        ...,
    ]

    demand_id: str = field(
        init=False
    )

    resource_selected: bool = False
    provider_selected: bool = False
    model_selected: bool = False
    execution_authorized: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "contract_id",
            _required_text(
                self.contract_id,
                "contract_id",
            ),
        )

        rows = tuple(
            sorted(
                self.demands,
                key=lambda item: (
                    item.capability_id
                ),
            )
        )

        if not rows:
            raise MissionAnalysisIncompleteError(
                "Mission capability demand "
                "must not be empty."
            )

        if not all(
            isinstance(
                item,
                CapabilityDemand,
            )
            for item in rows
        ):
            raise TypeError(
                "demands must contain "
                "CapabilityDemand only."
            )

        ids = [
            item.capability_id
            for item in rows
        ]

        if len(ids) != len(set(ids)):
            raise MissionFoundationInvariantError(
                "Capability demands "
                "must be unique."
            )

        object.__setattr__(
            self,
            "demands",
            rows,
        )

        for name in (
            "resource_selected",
            "provider_selected",
            "model_selected",
            "execution_authorized",
            "system_truth_asserted",
        ):
            if getattr(
                self,
                name,
            ) is not False:
                raise MissionFoundationInvariantError(
                    "Mission analysis cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "demand_id",
            _stable_id(
                "MCD",
                {
                    "contract_id": (
                        self.contract_id
                    ),
                    "demands": [
                        item.to_dict()
                        for item in rows
                    ],
                },
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_MISSION_FOUNDATION_VERSION
            ),
            "demand_id": self.demand_id,
            "contract_id": (
                self.contract_id
            ),
            "demands": [
                item.to_dict()
                for item in self.demands
            ],
            "resource_selected": False,
            "provider_selected": False,
            "model_selected": False,
            "execution_authorized": False,
            "system_truth_asserted": False,
        }


@dataclass(
    frozen=True,
    slots=True,
)
class CouncilCapabilityBinding:
    council_id: str
    capabilities: tuple[
        str,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        council_id = _required_text(
            self.council_id,
            "council_id",
        )

        known = {
            council.value
            for council in COUNCILS
        }

        if council_id not in known:
            raise MissionFoundationInvariantError(
                "CouncilCapabilityBinding "
                "requires an existing "
                "Genesis Council."
            )

        object.__setattr__(
            self,
            "council_id",
            council_id,
        )

        object.__setattr__(
            self,
            "capabilities",
            _normalized_tuple(
                self.capabilities,
                "capability",
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class CouncilGraphNode:
    council_id: str
    roles: tuple[
        str,
        ...,
    ]

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "council_id",
            _required_text(
                self.council_id,
                "council_id",
            ),
        )

        object.__setattr__(
            self,
            "roles",
            _normalized_tuple(
                self.roles,
                "role",
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "council_id": self.council_id,
            "roles": list(
                self.roles
            ),
        }


@dataclass(
    frozen=True,
    slots=True,
)
class GovernedCouncilGraph:
    contract_id: str
    demand_id: str

    nodes: tuple[
        CouncilGraphNode,
        ...,
    ]

    capability_owners: tuple[
        tuple[
            str,
            str,
        ],
        ...,
    ]

    graph_id: str = field(
        init=False
    )

    council_activated: bool = False
    execution_requested: bool = False
    execution_authorized: bool = False
    resource_selected: bool = False
    system_truth_asserted: bool = False

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "contract_id",
            _required_text(
                self.contract_id,
                "contract_id",
            ),
        )

        object.__setattr__(
            self,
            "demand_id",
            _required_text(
                self.demand_id,
                "demand_id",
            ),
        )

        nodes = tuple(
            sorted(
                self.nodes,
                key=lambda item: (
                    item.council_id
                ),
            )
        )

        if not nodes:
            raise CouncilGraphIncompleteError(
                "Council graph "
                "must not be empty."
            )

        if not all(
            isinstance(
                item,
                CouncilGraphNode,
            )
            for item in nodes
        ):
            raise TypeError(
                "nodes must contain "
                "CouncilGraphNode only."
            )

        council_ids = [
            item.council_id
            for item in nodes
        ]

        if len(council_ids) != len(
            set(council_ids)
        ):
            raise MissionFoundationInvariantError(
                "Council graph nodes "
                "must be unique."
            )

        owners = tuple(
            sorted(
                (
                    _required_text(
                        capability,
                        "capability_id",
                    ),
                    _required_text(
                        council,
                        "owner_council_id",
                    ),
                )
                for capability, council
                in self.capability_owners
            )
        )

        if not owners:
            raise CouncilGraphIncompleteError(
                "Council graph requires "
                "capability ownership."
            )

        capabilities = [
            capability
            for capability, _ in owners
        ]

        if len(capabilities) != len(
            set(capabilities)
        ):
            raise MissionFoundationInvariantError(
                "Capability ownership "
                "must be unique."
            )

        known_nodes = set(
            council_ids
        )

        for _, owner in owners:
            if owner not in known_nodes:
                raise MissionFoundationInvariantError(
                    "Capability owner must "
                    "exist in Council graph."
                )

        required_governance = {
            "EX",
            "AY",
        }

        if not required_governance.issubset(
            known_nodes
        ):
            raise CouncilGraphIncompleteError(
                "Council graph requires "
                "EX routing authority and "
                "AY acceptance authority."
            )

        object.__setattr__(
            self,
            "nodes",
            nodes,
        )

        object.__setattr__(
            self,
            "capability_owners",
            owners,
        )

        for name in (
            "council_activated",
            "execution_requested",
            "execution_authorized",
            "resource_selected",
            "system_truth_asserted",
        ):
            if getattr(
                self,
                name,
            ) is not False:
                raise MissionFoundationInvariantError(
                    "Council graph cannot "
                    f"assert {name}."
                )

        object.__setattr__(
            self,
            "graph_id",
            _stable_id(
                "MCG",
                {
                    "contract_id": (
                        self.contract_id
                    ),
                    "demand_id": (
                        self.demand_id
                    ),
                    "nodes": [
                        item.to_dict()
                        for item in nodes
                    ],
                    "capability_owners": [
                        list(item)
                        for item in owners
                    ],
                },
            ),
        )

    def to_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "version": (
                GOVERNED_MISSION_FOUNDATION_VERSION
            ),
            "graph_id": self.graph_id,
            "contract_id": (
                self.contract_id
            ),
            "demand_id": self.demand_id,
            "nodes": [
                item.to_dict()
                for item in self.nodes
            ],
            "capability_owners": [
                list(item)
                for item
                in self.capability_owners
            ],
            "council_activated": False,
            "execution_requested": False,
            "execution_authorized": False,
            "resource_selected": False,
            "system_truth_asserted": False,
        }


class GovernedMissionFoundation:
    @staticmethod
    def analyze(
        contract: MissionContract,
        rules: Iterable[
            CapabilityRule
        ],
    ) -> MissionCapabilityDemand:
        if not isinstance(
            contract,
            MissionContract,
        ):
            raise TypeError(
                "contract must be "
                "MissionContract."
            )

        rows = tuple(
            rules
        )

        if not rows:
            raise MissionAnalysisIncompleteError(
                "Mission analysis requires "
                "explicit capability rules."
            )

        if not all(
            isinstance(
                item,
                CapabilityRule,
            )
            for item in rows
        ):
            raise TypeError(
                "rules must contain "
                "CapabilityRule only."
            )

        rule_ids = [
            item.rule_id
            for item in rows
        ]

        if len(rule_ids) != len(
            set(rule_ids)
        ):
            raise MissionFoundationInvariantError(
                "Capability rule IDs "
                "must be unique."
            )

        corpus = " ".join(
            (
                contract.objective,
                contract.scope,
                contract.requested_output,
                *contract.constraints,
                *contract.acceptance_criteria,
                *contract.evidence_obligations,
            )
        ).casefold()

        by_capability: dict[
            str,
            list[CapabilityRule],
        ] = {}

        for rule in rows:
            if any(
                keyword in corpus
                for keyword in rule.keywords
            ):
                by_capability.setdefault(
                    rule.capability_id,
                    [],
                ).append(
                    rule
                )

        if not by_capability:
            raise MissionAnalysisIncompleteError(
                "Mission capability demand "
                "cannot be derived from "
                "the supplied rules."
            )

        demands = tuple(
            CapabilityDemand(
                capability_id=capability,
                matched_rule_ids=tuple(
                    item.rule_id
                    for item in matched
                ),
                rationales=tuple(
                    item.rationale
                    for item in matched
                ),
            )
            for capability, matched
            in sorted(
                by_capability.items()
            )
        )

        return MissionCapabilityDemand(
            contract_id=(
                contract.contract_id
            ),
            demands=demands,
        )

    @staticmethod
    def synthesize_council_graph(
        contract: MissionContract,
        demand: MissionCapabilityDemand,
        bindings: Iterable[
            CouncilCapabilityBinding
        ],
    ) -> GovernedCouncilGraph:
        if not isinstance(
            contract,
            MissionContract,
        ):
            raise TypeError(
                "contract must be "
                "MissionContract."
            )

        if not isinstance(
            demand,
            MissionCapabilityDemand,
        ):
            raise TypeError(
                "demand must be "
                "MissionCapabilityDemand."
            )

        if (
            demand.contract_id
            != contract.contract_id
        ):
            raise MissionFoundationInvariantError(
                "Capability demand is not "
                "bound to the supplied "
                "mission contract."
            )

        rows = tuple(
            bindings
        )

        if not rows:
            raise CouncilGraphIncompleteError(
                "Council graph synthesis "
                "requires explicit bindings."
            )

        if not all(
            isinstance(
                item,
                CouncilCapabilityBinding,
            )
            for item in rows
        ):
            raise TypeError(
                "bindings must contain "
                "CouncilCapabilityBinding only."
            )

        ids = [
            item.council_id
            for item in rows
        ]

        if len(ids) != len(set(ids)):
            raise MissionFoundationInvariantError(
                "Council bindings must "
                "be unique by council."
            )

        required = {
            item.capability_id
            for item in demand.demands
        }

        coverage = {
            item.council_id: (
                set(
                    item.capabilities
                )
                & required
            )
            for item in rows
        }

        coverage = {
            council: caps
            for council, caps
            in coverage.items()
            if caps
        }

        covered = set().union(
            *coverage.values()
        ) if coverage else set()

        missing = tuple(
            sorted(
                required - covered
            )
        )

        if missing:
            raise CouncilGraphIncompleteError(
                "No existing Council binding "
                "covers capabilities: "
                + ", ".join(missing)
            )

        candidates = tuple(
            sorted(
                coverage
            )
        )

        selected: tuple[
            str,
            ...,
        ] | None = None

        for size in range(
            1,
            len(candidates) + 1,
        ):
            valid = []

            for combo in itertools.combinations(
                candidates,
                size,
            ):
                union = set().union(
                    *(
                        coverage[
                            council
                        ]
                        for council in combo
                    )
                )

                if union == required:
                    valid.append(
                        tuple(combo)
                    )

            if valid:
                selected = min(
                    valid
                )
                break

        if selected is None:
            raise CouncilGraphIncompleteError(
                "Unable to synthesize "
                "complete Council coverage."
            )

        capability_owners = []

        for capability in sorted(
            required
        ):
            owners = [
                council
                for council in selected
                if capability
                in coverage[council]
            ]

            if not owners:
                raise CouncilGraphIncompleteError(
                    "Selected Council graph "
                    "lost capability coverage."
                )

            capability_owners.append(
                (
                    capability,
                    min(owners),
                )
            )

        node_roles: dict[
            str,
            set[str],
        ] = {
            "EX": {
                "MISSION_ROUTING_AUTHORITY",
            },
            "AY": {
                "ACCEPTANCE_AUTHORITY",
            },
        }

        for council in selected:
            node_roles.setdefault(
                council,
                set(),
            ).add(
                "CAPABILITY_WORKER"
            )

        nodes = tuple(
            CouncilGraphNode(
                council_id=council,
                roles=tuple(
                    sorted(
                        roles
                    )
                ),
            )
            for council, roles
            in sorted(
                node_roles.items()
            )
        )

        return GovernedCouncilGraph(
            contract_id=(
                contract.contract_id
            ),
            demand_id=(
                demand.demand_id
            ),
            nodes=nodes,
            capability_owners=tuple(
                capability_owners
            ),
        )


__all__ = [
    "GOVERNED_MISSION_FOUNDATION_VERSION",
    "MissionFoundationInvariantError",
    "MissionAnalysisIncompleteError",
    "CouncilGraphIncompleteError",
    "MissionContract",
    "CapabilityRule",
    "CapabilityDemand",
    "MissionCapabilityDemand",
    "CouncilCapabilityBinding",
    "CouncilGraphNode",
    "GovernedCouncilGraph",
    "GovernedMissionFoundation",
]
