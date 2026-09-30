from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Iterable

from maestro.enums import CouncilId, DagNodeState


class DagError(RuntimeError):
    pass


class DagCycleError(DagError):
    pass


class DagDependencyError(DagError):
    pass


@dataclass(slots=True)
class DagNode:
    node_id: str
    council: CouncilId
    action: str
    criteria_ids: list[str] = field(default_factory=list)
    depends_on: set[str] = field(default_factory=set)
    state: DagNodeState = DagNodeState.PENDING
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "council": self.council.value,
            "action": self.action,
            "criteria_ids": list(self.criteria_ids),
            "depends_on": sorted(self.depends_on),
            "state": self.state.value,
            "output": self.output,
            "error": self.error,
        }


@dataclass
class DagEngine:
    nodes: dict[str, DagNode] = field(default_factory=dict)

    def add_node(self, node: DagNode) -> None:
        if node.node_id in self.nodes:
            raise DagError(f"Duplicate DAG node: {node.node_id}")
        self.nodes[node.node_id] = node

    def add_dependency(self, node_id: str, dependency_id: str) -> None:
        if node_id not in self.nodes or dependency_id not in self.nodes:
            raise DagDependencyError("Both DAG nodes must exist before adding dependency.")
        if node_id == dependency_id:
            raise DagCycleError("A DAG node cannot depend on itself.")
        self.nodes[node_id].depends_on.add(dependency_id)
        self.validate_acyclic()

    def validate_dependencies_exist(self) -> None:
        for node in self.nodes.values():
            missing = node.depends_on - set(self.nodes)
            if missing:
                raise DagDependencyError(
                    f"{node.node_id} has missing dependencies: {sorted(missing)}"
                )

    def validate_acyclic(self) -> None:
        self.validate_dependencies_exist()

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            if node_id in visiting:
                raise DagCycleError(f"Cycle detected at {node_id}")

            visiting.add(node_id)
            for dep in self.nodes[node_id].depends_on:
                visit(dep)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in self.nodes:
            visit(node_id)

    def topological_order(self) -> list[str]:
        self.validate_acyclic()
        indegree = {node_id: 0 for node_id in self.nodes}
        children: dict[str, set[str]] = {node_id: set() for node_id in self.nodes}

        for node in self.nodes.values():
            indegree[node.node_id] = len(node.depends_on)
            for dep in node.depends_on:
                children[dep].add(node.node_id)

        queue = sorted([node_id for node_id, degree in indegree.items() if degree == 0])
        order: list[str] = []

        while queue:
            current = queue.pop(0)
            order.append(current)
            for child in sorted(children[current]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
                    queue.sort()

        if len(order) != len(self.nodes):
            raise DagCycleError("Cycle detected while calculating topological order.")
        return order

    def _refresh_blocked_states(self) -> None:
        terminal_bad = {DagNodeState.FAILED, DagNodeState.BLOCKED}
        changed = True
        while changed:
            changed = False
            for node in self.nodes.values():
                if node.state in {
                    DagNodeState.SUCCEEDED,
                    DagNodeState.FAILED,
                    DagNodeState.BLOCKED,
                    DagNodeState.SKIPPED,
                }:
                    continue
                if any(self.nodes[dep].state in terminal_bad for dep in node.depends_on):
                    node.state = DagNodeState.BLOCKED
                    node.error = "Blocked by failed dependency."
                    changed = True

    def ready_nodes(self) -> list[DagNode]:
        self._refresh_blocked_states()
        ready: list[DagNode] = []
        for node_id in self.topological_order():
            node = self.nodes[node_id]
            if node.state not in {DagNodeState.PENDING, DagNodeState.READY}:
                continue
            if all(self.nodes[dep].state is DagNodeState.SUCCEEDED for dep in node.depends_on):
                node.state = DagNodeState.READY
                ready.append(node)
        return ready

    def start(self, node_id: str, actor: CouncilId) -> DagNode:
        if actor is not CouncilId.EX:
            raise PermissionError("Only EX may start a governed DAG node.")
        node = self.nodes[node_id]
        if node not in self.ready_nodes() and node.state is not DagNodeState.READY:
            raise DagError(f"Node {node_id} is not ready.")
        node.state = DagNodeState.RUNNING
        return node

    def succeed(self, node_id: str, output: dict[str, Any] | None = None) -> None:
        node = self.nodes[node_id]
        if node.state is not DagNodeState.RUNNING:
            raise DagError(f"Node {node_id} must be RUNNING before success.")
        node.output = output or {}
        node.state = DagNodeState.SUCCEEDED
        node.error = None

    def fail(self, node_id: str, error: str) -> None:
        node = self.nodes[node_id]
        if node.state is not DagNodeState.RUNNING:
            raise DagError(f"Node {node_id} must be RUNNING before failure.")
        node.state = DagNodeState.FAILED
        node.error = error
        self._refresh_blocked_states()

    def retry(self, node_id: str, actor: CouncilId) -> None:
        if actor is not CouncilId.EX:
            raise PermissionError("Only EX may reset a DAG node for retry.")
        node = self.nodes[node_id]
        if node.state is not DagNodeState.FAILED:
            raise DagError("Only FAILED nodes may be retried.")
        node.state = DagNodeState.PENDING
        node.error = None

        # Descendants that were blocked only because of this failure can be reconsidered.
        for other in self.nodes.values():
            if other.state is DagNodeState.BLOCKED:
                other.state = DagNodeState.PENDING
                other.error = None
        self._refresh_blocked_states()

    def complete(self) -> bool:
        return bool(self.nodes) and all(
            node.state in {DagNodeState.SUCCEEDED, DagNodeState.SKIPPED}
            for node in self.nodes.values()
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "topological_order": self.topological_order() if self.nodes else [],
        }

    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> "DagEngine":
        engine = cls()
        for node_id, raw in snapshot.get("nodes", {}).items():
            engine.add_node(
                DagNode(
                    node_id=node_id,
                    council=CouncilId(raw["council"]),
                    action=raw["action"],
                    criteria_ids=list(raw.get("criteria_ids", [])),
                    depends_on=set(raw.get("depends_on", [])),
                    state=DagNodeState(raw["state"]),
                    output=dict(raw.get("output", {})),
                    error=raw.get("error"),
                )
            )
        engine.validate_acyclic()
        return engine
