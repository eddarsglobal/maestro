from __future__ import annotations

from dataclasses import replace

from .provider_contracts import (
    ResearchCapability,
    ResearchProviderDescriptor,
    ResearchProviderStatus,
)


class ResearchProviderRegistry:
    """
    Provider-neutral RX research catalog.

    This registry stores routing descriptors only.
    It cannot execute providers.

    Actual source access must cross MAESTRO's
    governed ToolRegistry / ActionFirewall boundary.
    """

    def __init__(self):
        self._descriptors: dict[
            str,
            ResearchProviderDescriptor,
        ] = {}

    def register(
        self,
        descriptor: ResearchProviderDescriptor,
    ) -> None:
        if not isinstance(
            descriptor,
            ResearchProviderDescriptor,
        ):
            raise TypeError(
                "descriptor must be a "
                "ResearchProviderDescriptor."
            )

        if (
            descriptor.provider_id
            in self._descriptors
        ):
            raise ValueError(
                "Duplicate research provider: "
                f"{descriptor.provider_id}"
            )

        self._descriptors[
            descriptor.provider_id
        ] = descriptor

    def unregister(
        self,
        provider_id: str,
    ) -> None:
        self._descriptors.pop(
            provider_id,
            None,
        )

    def descriptor(
        self,
        provider_id: str,
    ) -> ResearchProviderDescriptor:
        return self._descriptors[
            provider_id
        ]

    def set_status(
        self,
        provider_id: str,
        status: ResearchProviderStatus,
    ) -> None:
        if not isinstance(
            status,
            ResearchProviderStatus,
        ):
            raise TypeError(
                "status must be a "
                "ResearchProviderStatus."
            )

        current = self._descriptors[
            provider_id
        ]

        self._descriptors[
            provider_id
        ] = replace(
            current,
            status=status,
        )

    def eligible(
        self,
        capability: ResearchCapability,
        *,
        forbidden_provider_ids: (
            frozenset[str]
        ) = frozenset(),
    ) -> list[
        ResearchProviderDescriptor
    ]:
        if not isinstance(
            capability,
            ResearchCapability,
        ):
            raise TypeError(
                "capability must be a "
                "ResearchCapability."
            )

        forbidden = frozenset(
            forbidden_provider_ids
        )

        out = []

        for descriptor in (
            self._descriptors.values()
        ):
            if (
                descriptor.provider_id
                in forbidden
            ):
                continue

            if (
                descriptor.status
                is ResearchProviderStatus.UNAVAILABLE
            ):
                continue

            if (
                capability
                not in descriptor.capabilities
            ):
                continue

            out.append(descriptor)

        return sorted(
            out,
            key=lambda item: (
                item.provider_id
            ),
        )

    def all(
        self,
    ) -> list[
        ResearchProviderDescriptor
    ]:
        return sorted(
            self._descriptors.values(),
            key=lambda item: (
                item.provider_id
            ),
        )
