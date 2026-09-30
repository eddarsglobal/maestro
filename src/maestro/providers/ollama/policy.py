from __future__ import annotations
from enum import StrEnum
from .models import OllamaModelInfo

class TaskClass(StrEnum):
    DIRECT = "DIRECT"
    GENERAL = "GENERAL"
    CODE = "CODE"
    HEAVY_CODE = "HEAVY_CODE"
    HEAVY_REASONING = "HEAVY_REASONING"
    MULTIMODAL = "MULTIMODAL"
    EMBEDDING = "EMBEDDING"

class LocalModelPolicy:
    """
    Capability-first bootstrap selector.
    Academy/Adaptive MAESTRO may later propose better choices from measurements.
    """

    def select(self, task_class: TaskClass, models: list[OllamaModelInfo]) -> OllamaModelInfo:
        if not models:
            raise LookupError("No local models discovered.")

        def has(m, cap): return cap in m.capabilities

        if task_class is TaskClass.EMBEDDING:
            candidates = [m for m in models if has(m, "embedding")]
        elif task_class is TaskClass.MULTIMODAL:
            candidates = [m for m in models if has(m, "vision")]
        elif task_class in {TaskClass.CODE, TaskClass.HEAVY_CODE}:
            candidates = [m for m in models if has(m, "completion") and ("coder" in m.name.lower())]
        else:
            candidates = [m for m in models if has(m, "completion")]

        if not candidates:
            candidates = list(models)

        # Default bootstrap: choose the smallest capable model.
        # Quality-aware promotion belongs to Academy/Adaptive policy.
        return min(candidates, key=lambda m: (m.size if m.size > 0 else 2**63, m.name))
