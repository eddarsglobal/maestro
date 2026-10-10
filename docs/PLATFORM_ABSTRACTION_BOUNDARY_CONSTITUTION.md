# MAESTRO Platform Abstraction Boundary Constitution

> Governing contract for keeping platform-specific discovery and execution behind generic governed interfaces.

## Status

This constitution formalizes BordingMap point `BMF-015`.

It governs the dependency direction between MAESTRO generic Core contracts and platform-, provider-, runtime-, hardware-, protocol-, operating-system-, and technology-specific implementations.

## PAB-01 — Generic Core never depends on contemporary technology identity

MAESTRO generic Core SHALL NOT require a specific provider, model family, runtime, operating system, accelerator, hardware class, protocol, platform, or technology product as part of its identity.

Known technologies SHALL remain adapter-edge data.

Unknown future technologies SHALL be admissible through the same generic contracts without constitutional redesign.

## PAB-02 — Dependency direction is platform edge toward generic Core contracts

The permitted architectural direction is:

```text
PLATFORM-SPECIFIC EDGE
        ↓
GENERIC DISCOVERY / ADAPTER CONTRACT
        ↓
GOVERNED MAESTRO BOUNDARY
```

Generic Core SHALL NOT import platform/provider implementations merely to expose its contracts.

## PAB-03 — Platform discovery must become generic before crossing the boundary

Raw platform discovery objects SHALL NOT cross into governed Core semantics.

Platform observations SHALL first become provider-neutral host, capability, and resource observations and then a `GenericDiscoveryProjection`.

`GovernedPlatformBoundary.accept_discovery()` SHALL accept only a generic projection.

```text
DISCOVERY != TRUST != INSTALL != ACTIVATE != EXECUTE
```

## PAB-04 — Platform adapter metadata must cross GAR before execution compatibility

A platform-specific executable adapter SHALL NOT enter a Core execution registry before its generic resource and adapter metadata have passed the generic adapter contract.

The governed crossing SHALL use `GenericResourceDescriptor`, `GenericAdapterDescriptor`, and `GovernedPlatformBoundary.validate_adapter()`.

Adapter validation SHALL NOT execute the adapter.

## PAB-05 — Platform identity is edge data, not constitutional identity

Platform identity MAY be recorded by `PlatformIdentity` for evidence, diagnostics, compatibility, routing metadata, or boundary attribution.

Platform identity SHALL NOT become a required MAESTRO Core identity, closed enum of supported technologies, or prerequisite for sovereign boot.

## PAB-06 — Execution handoff is metadata, not authority

After generic validation, MAESTRO MAY construct a `PlatformExecutionHandoff` describing platform, resource, adapter, and capability identity.

```text
HANDOFF != EXECUTION
HANDOFF != ACTIVATION
HANDOFF != NETWORK AUTHORIZATION
HANDOFF != SYSTEM TRUTH
```

The handoff SHALL contain no executable adapter object.

## PAB-07 — Legacy compatibility may exist only after the governed boundary

Legacy execution registries and compatibility bridges MAY remain temporarily available when required for compatibility.

They SHALL receive platform-specific executable objects only after generic discovery admission and generic adapter validation have succeeded.

Compatibility SHALL NOT be used to bypass the governed platform boundary.

## PAB-08 — Sovereign boot is zero-platform by default

MAESTRO SHALL remain bootable and governable with zero provider or platform resource loaded.

Production Genesis SHALL NOT silently instantiate a contemporary provider as a default identity dependency.

Platform compatibility facades MAY be exposed explicitly or lazily, but SHALL NOT cause provider modules to load merely because generic Core is imported.

## PAB-09 — Platform-boundary decisions are passive and fail closed

The platform boundary SHALL perform no provider invocation, adapter execution, network access, installation, activation, learning, promotion, or system-truth assertion.

Raw discovery leakage, undeclared capabilities, inconsistent generic descriptors, invalid bindings, authority escalation, and dependency inversion SHALL fail closed.

## PAB-10 — BMF-015 requires both abstraction and actual edge conformance

The existence of generic contracts alone is insufficient for BMF-015.

Every certified platform-specific discovery/execution edge within the certification scope SHALL either:

1. remain fully outside Core and cross through the generic governed contracts; or
2. be explicitly classified as a compatibility edge whose crossing order is proven to place generic governance before legacy registration.

Physical relocation of platform code without governed contract traversal SHALL NOT satisfy BMF-015.

## Canonical discovery path

```text
platform-specific observation
        ↓
CapabilityObservation / ResourceObservation / HostDiscoveryObservation
        ↓
GenericHostDiscoveryProjector
        ↓
GenericDiscoveryProjection
        ↓
GovernedPlatformBoundary.accept_discovery()
```

## Canonical adapter path

```text
platform-specific adapter metadata
        ↓
GenericResourceDescriptor
        +
GenericAdapterDescriptor
        ↓
GovernedPlatformBoundary.validate_adapter()
        ↓
PlatformExecutionHandoff
```

## Compatibility ordering law

If a historical executable registry remains in use, the ordering SHALL be:

```text
GENERIC DISCOVERY PROJECTION
        ↓
PAB DISCOVERY ACCEPTANCE
        ↓
GENERIC ADAPTER VALIDATION
        ↓
PAB EXECUTION HANDOFF
        ↓
LEGACY COMPATIBILITY REGISTRATION
```

Legacy registration SHALL be last.

## Current compatibility edge

The current Ollama implementation is adapter data and provider-edge compatibility code.

Its name, protocol, model family, runtime behavior, and availability are not MAESTRO constitutional knowledge.

The Core remains valid if Ollama is absent, replaced, unavailable, or obsolete.

## Required evidence

A BMF-015 checkpoint SHALL demonstrate at minimum:

1. zero provider-module load for ordinary generic Core imports;
2. zero provider import in generic discovery, generic adapters, PAB, Genesis, and sovereign generic bridge;
3. zero default platform binding in Genesis;
4. raw platform discovery cannot cross PAB;
5. platform discovery crosses as `GenericDiscoveryProjection`;
6. platform adapter metadata crosses through GAR/PAB;
7. platform identity remains edge data;
8. execution handoff grants no execution authority;
9. executable platform objects do not enter compatibility registration before PAB validation;
10. current provider-edge compatibility tests remain green;
11. unknown/future platform identifiers remain admissible;
12. generic Core tests remain green;
13. BordingMap point `BMF-015` is explicitly assessed with evidence.

## Final invariants

> PLATFORM IDENTITY = ADAPTER DATA, NOT MAESTRO IDENTITY.

> GENERIC CORE SHALL NOT DEPEND ON PLATFORM IMPLEMENTATIONS.

> DISCOVERY != TRUST. BINDING != EXECUTION. HANDOFF != AUTHORIZATION.
