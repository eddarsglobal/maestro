# MAESTRO Generic Discovery Descriptor Constitution

> Governing contract for technology-independent host, resource, and capability discovery representations.

## Status

This constitution formalizes BordingMap point `BMF-007`.

BMF-007 requires host discovery to produce generic capability and resource descriptors without binding MAESTRO identity to the technologies of one era.

## GDR-01 — Discovery speaks generic descriptors

Host discovery SHALL project observations into generic host, resource, and capability descriptors.

Discovery output is data, not authority.

## GDR-02 — Host identity is technology-independent

`HostDescriptor` SHALL describe a host boundary without requiring any contemporary machine, cloud, runtime, accelerator, operating system, protocol, or provider identity.

An unknown future host class SHALL remain representable.

## GDR-03 — Resource identity is technology-independent

`GenericResourceDescriptor` SHALL NOT require `provider_id`, `model_id`, or `runtime_id`.

A resource may represent any future technological resource class that can be observed and described.

## GDR-04 — Capability identity is extensible

`CapabilityDescriptor` SHALL use extensible capability identifiers rather than require membership in a closed technology-era capability enum.

Unknown future capabilities SHALL remain representable without changing MAESTRO constitutional identity.

## GDR-05 — Discovery observation is separate from execution

`HostDiscoveryObservation` records passive evidence supplied by a probe or adapter.

The generic projector SHALL NOT itself probe networks, execute tools, launch processes, install software, activate resources, or route work.

```text
OBSERVE
    !=
EXECUTE

DESCRIBE
    !=
ACTIVATE
```

## GDR-06 — Projection is deterministic

Equivalent host observations SHALL produce equivalent generic descriptor projections.

Capability and resource collections SHALL use deterministic ordering in projected output.

## GDR-07 — Referential integrity is fail-closed

Duplicate capability identifiers SHALL be rejected.

Duplicate resource identifiers SHALL be rejected.

A resource SHALL NOT claim a capability that is absent from the same host observation.

## GDR-08 — Descriptors are immutable observations

Generic descriptors SHALL be immutable after construction.

Descriptor metadata SHALL not provide a hidden mutable authority channel.

## GDR-09 — Discovery grants no authority

Producing a host, resource, or capability descriptor SHALL NOT grant trust, installation, activation, routing, execution, promotion, AY verdict, EX authorization, or system truth.

```text
DISCOVERED
    !=
TRUSTED
    !=
INSTALLED
    !=
ACTIVATED
    !=
AUTHORIZED
```

## GDR-10 — Technological-time sovereignty

MAESTRO SHALL be able to describe technologies that did not exist when this version was written.

Known providers, model families, runtimes, hardware classes, and protocols are adapter data, not constitutional knowledge.

## BordingMap boundary

```text
BMF-005 = zero-resource sovereign boot
BMF-006 = explicit degraded intelligence capability state
BMF-007 = host discovery produces generic capability and resource descriptors
```

BMF-007 does not yet certify automatic external landscape discovery, trust, installation, integration, activation, or execution.

## Required generic objects

```text
CapabilityDescriptor
HostDescriptor
GenericResourceDescriptor

CapabilityObservation
ResourceObservation
HostDiscoveryObservation

GenericHostDiscoveryProjector
GenericDiscoveryProjection
```

## Evidence requirements

A checkpoint claiming BMF-007 conformance SHALL demonstrate at least:

1. host observations produce `HostDescriptor`;
2. host observations produce `CapabilityDescriptor` objects;
3. host observations produce `GenericResourceDescriptor` objects;
4. provider identity is not required by generic resources;
5. model identity is not required by generic resources;
6. runtime identity is not required by generic resources;
7. unknown future capability identifiers are accepted;
8. projection order is deterministic;
9. duplicate capability observations fail closed;
10. duplicate resource observations fail closed;
11. undeclared resource capabilities fail closed;
12. projection performs no network or process activity;
13. discovery output grants no authority;
14. BordingMap point `BMF-007` is explicitly assessed with evidence.

## Final invariant

> MAESTRO describes what exists through capability and resource contracts before it reasons about how, whether, or with what authority that technology may be used.
