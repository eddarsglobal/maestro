from __future__ import annotations

from dataclasses import dataclass

from maestro.storage.object_store import BinaryObjectStore, ObjectRef
from .models import AcademyScenario, ScenarioResult


SCENARIO_TYPE = 0x41
RESULT_TYPE = 0x42


class AcademyCorpus:
    """
    Heavy Academy material is kept in the binary object store.
    The Academy keeps references instead of resident copies.
    """

    def __init__(self, objects: BinaryObjectStore):
        self.objects = objects
        self.scenarios: dict[str, ObjectRef] = {}
        self.results: dict[tuple[str, str], ObjectRef] = {}

    def put_scenario(self, scenario: AcademyScenario) -> ObjectRef:
        ref = self.objects.put(SCENARIO_TYPE, scenario.to_dict())
        self.scenarios[scenario.scenario_id] = ref
        return ref

    def put_result(self, result: ScenarioResult) -> ObjectRef:
        ref = self.objects.put(RESULT_TYPE, result.to_dict())
        self.results[(result.scenario_id, result.policy_id)] = ref
        return ref
