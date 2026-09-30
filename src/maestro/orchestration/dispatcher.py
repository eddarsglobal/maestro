from __future__ import annotations

from dataclasses import dataclass, field

from maestro.constitution import validate_routing_request
from maestro.enums import CouncilId
from maestro.models import RoutingRequest


@dataclass(slots=True)
class DispatchRecord:
    task_id: str
    requested_by: CouncilId
    target: CouncilId
    action: str
    reason: str


@dataclass
class Dispatcher:
    history: list[DispatchRecord] = field(default_factory=list)

    def dispatch(self, request: RoutingRequest, actor: CouncilId) -> list[DispatchRecord]:
        if actor is not CouncilId.EX:
            raise PermissionError("Only EX can execute a routing request.")

        validate_routing_request(request)

        records: list[DispatchRecord] = []
        for target in request.targets:
            record = DispatchRecord(
                task_id=request.task_id,
                requested_by=request.requested_by,
                target=target,
                action=request.action,
                reason=request.reason,
            )
            self.history.append(record)
            records.append(record)

        return records
