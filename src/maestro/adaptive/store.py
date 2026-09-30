from __future__ import annotations

from dataclasses import dataclass

from maestro.storage.object_store import BinaryObjectStore, ObjectRef
from .models import AdaptivePolicy, PolicyKind, PolicyStatus


POLICY_OBJECT_TYPE = 0x51


@dataclass(frozen=True, slots=True)
class PolicyRef:
    policy_id: str
    object_ref: ObjectRef


class AdaptivePolicyStore:
    """
    Immutable content-addressed persistence for policy versions.
    """

    def __init__(self, objects: BinaryObjectStore):
        self.objects = objects
        self._refs: dict[str, ObjectRef] = {}

    def put(self, policy: AdaptivePolicy) -> PolicyRef:
        ref = self.objects.put(POLICY_OBJECT_TYPE, policy.to_dict())
        self._refs[policy.policy_id] = ref
        return PolicyRef(policy.policy_id, ref)

    def raw(self, policy_id: str) -> dict:
        return self.objects.get(self._refs[policy_id])
