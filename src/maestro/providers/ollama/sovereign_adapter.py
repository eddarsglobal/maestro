from __future__ import annotations

from maestro.autonomous.provider_adapters import ProviderRequest
from maestro.sovereign.contracts import (
    IntelligenceRequest,
    IntelligenceResponse,
    IntelligenceCapability,
    ResourceDescriptor,
)
from .provider import OllamaProviderAdapter
from .models import OllamaModelInfo


class OllamaSovereignResourceAdapter:
    provider_id = "ollama"

    def __init__(self, model: OllamaModelInfo, provider: OllamaProviderAdapter):
        self.model = model
        self.provider = provider
        self.model_id = model.name
        self.resource_id = f"ollama::{model.name}"

    def execute(self, request: IntelligenceRequest) -> IntelligenceResponse:
        context = {}

        if request.context_ref is not None:
            context["context_ref"] = request.context_ref

        options = {}

        if request.max_tokens is not None:
            options["num_predict"] = int(request.max_tokens)

        execution_profile = request.execution_profile

        if execution_profile is not None:
            if execution_profile.temperature is not None:
                options["temperature"] = float(
                    execution_profile.temperature
                )

            if execution_profile.seed is not None:
                options["seed"] = int(execution_profile.seed)

        if options:
            context["options"] = options

        # MAESTRO owns reasoning depth.
        # Provider/model defaults must not silently spend cognitive mass.
        advertised = set(self.model.capabilities)

        if "thinking" in advertised:
            model_name = self.model.name.lower()

            if model_name.startswith("gpt-oss"):
                # GPT-OSS cannot fully disable thinking.
                context["think"] = (
                    "high"
                    if request.capability == IntelligenceCapability.HEAVY_REASONING
                    else "low"
                )
            else:
                context["think"] = (
                    request.capability
                    == IntelligenceCapability.HEAVY_REASONING
                )

        if (
            execution_profile is not None
            and execution_profile.thinking is not None
        ):
            requested_thinking = execution_profile.thinking

            if (
                self.model.name.lower().startswith("gpt-oss")
                and requested_thinking is False
            ):
                context["think"] = "low"
            else:
                context["think"] = requested_thinking

        response = self.provider.generate(
            ProviderRequest(
                purpose=request.capability.value,
                model_id=self.model.name,
                instructions=request.instruction,
                context=context,
            )
        )
        return IntelligenceResponse(
            resource_id=self.resource_id,
            provider_id=self.provider_id,
            model_id=self.model.name,
            output=response.output,
            success=True,
            metadata={
                **dict(response.metadata),
                "think_policy": context.get("think"),
                "execution_profile": (
                    execution_profile.to_dict()
                    if execution_profile is not None
                    else None
                ),
                "execution_profile_ref": (
                    execution_profile.profile_ref
                    if execution_profile is not None
                    else None
                ),
                "deterministic_execution": bool(
                    execution_profile is not None
                    and execution_profile.deterministic
                ),
            },
        )


def descriptor_from_ollama(model: OllamaModelInfo) -> ResourceDescriptor:
    caps = set()

    name = model.name.lower()
    advertised = set(model.capabilities)

    has_completion = "completion" in advertised
    has_embedding = "embedding" in advertised

    # Embedding capability is independent.
    if has_embedding:
        caps.add(IntelligenceCapability.EMBEDDING)

    # Reasoning / tools / vision / audio are inference capabilities.
    # They are admitted only for models that can actually complete/generate.
    if has_completion:
        caps.add(IntelligenceCapability.DIRECT)
        caps.add(IntelligenceCapability.GENERAL_REASONING)

        if "thinking" in advertised:
            caps.add(IntelligenceCapability.HEAVY_REASONING)

        if "tools" in advertised:
            caps.add(IntelligenceCapability.TOOL_USE)

        if "vision" in advertised:
            caps.add(IntelligenceCapability.VISION)

        if "audio" in advertised:
            caps.add(IntelligenceCapability.AUDIO)

        if "coder" in name:
            caps.add(IntelligenceCapability.CODE)

            if model.size >= 10_000_000_000:
                caps.add(IntelligenceCapability.HEAVY_CODE)

    return ResourceDescriptor(
        resource_id=f"ollama::{model.name}",
        provider_id="ollama",
        model_id=model.name,
        capabilities=frozenset(caps),
        local=True,
        metadata={
            "size": model.size,
            "family": model.family,
            "parameter_size": model.parameter_size,
            "quantization_level": model.quantization_level,
            "context_length": model.context_length,
            "embedding_length": model.embedding_length,
        },
    )
