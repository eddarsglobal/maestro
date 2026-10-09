# MAESTRO Zero-Model Sovereignty Constitution

> Governing contract for sovereign MAESTRO boot when no intelligence resource is available.

## Status

This constitution formalizes BordingMap point `BMF-005`.

It does not introduce a new provider, model, runtime, network dependency, or execution authority.

The behavior certified by this checkpoint is:

```text
MAESTRO Core
    |
    +-- boots without an inference resource
    +-- performs no provider acquisition
    +-- performs no network request
    +-- performs no external-process launch
    +-- preserves governance and recovery
    +-- reports READY when the sovereign Core is healthy
```

## ZMS-01 — Boot independence

MAESTRO SHALL be able to initialize and start its sovereign control plane without requiring an inference model, model server, provider, or intelligence runtime.

## ZMS-02 — Absence is not failure

The absence of an intelligence resource SHALL be treated as a capability condition, not as a MAESTRO identity failure.

## ZMS-03 — No hidden inference

Zero-model boot SHALL NOT invoke inference implicitly.

## ZMS-04 — No implicit network

Zero-model boot SHALL NOT require or initiate network access merely to make the sovereign Core operational.

## ZMS-05 — No implicit acquisition

Zero-model boot SHALL NOT install, download, activate, or launch an intelligence resource.

```text
RESOURCE ABSENT
    !=
INSTALL RESOURCE
```

## ZMS-06 — Sovereign readiness

If Core invariants, durable recovery, governance, registry, and kernel boot requirements are satisfied, MAESTRO MAY report Core status `READY` even when no intelligence resource exists.

`READY` means the sovereign control plane is healthy.

It does not mean every optional intelligence capability is available.

## ZMS-07 — Fail closed on real Core conflicts

Zero-model sovereignty SHALL NOT weaken existing fail-closed behavior.

An unresolved durable Core conflict may prevent `READY`.

Absence of a model alone may not.

## ZMS-08 — Authority does not expand

Operating without an intelligence resource grants no new authority to MAESTRO, Councils, tools, adapters, providers, or the BordingMapControlAgent.

## ZMS-09 — Technology independence

No current provider, model family, runtime, accelerator, protocol, or commercial technology is part of this contract.

The contract is capability-based and must remain valid across future technology generations.

## ZMS-10 — Atomic boot

Zero-model boot SHOULD perform only the minimum deterministic work required to establish sovereign Core readiness and recovery state.

## Certified boundary

This checkpoint certifies only:

```text
ZERO INTELLIGENCE RESOURCE
        |
        v
SOVEREIGN CORE BOOT
        |
        v
READY OR FAIL-CLOSED FOR A REAL CORE REASON
```

It does not yet certify the richer degraded-capability report required by `BMF-006`.

Therefore:

```text
BMF-005 = Zero-resource sovereign boot
BMF-006 = Explicit degraded intelligence capability state
```

These boundaries MUST remain separate.

## Evidence requirements

A version claiming conformance with this constitution must demonstrate at least:

1. `ProductionGenesisSystem` has no direct required provider dependency.
2. a fresh temporary runtime can start with external network calls forbidden;
3. a fresh temporary runtime can start with external process creation forbidden;
4. the resulting healthy Core status is `READY`;
5. existing Genesis regression tests remain green;
6. the complete Core regression suite remains green;
7. BordingMap point `BMF-005` is explicitly assessed with evidence.

## Final invariant

> MAESTRO can exist before any model is present.

Models may extend MAESTRO's reachable intelligence.

They do not define MAESTRO's existence, sovereignty, or authority.
