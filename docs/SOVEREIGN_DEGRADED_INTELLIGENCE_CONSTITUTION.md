# MAESTRO Sovereign Degraded Intelligence Constitution

> Governing contract for explicit intelligence-capability state when the Sovereign Core remains healthy.

## Status

This constitution formalizes BordingMap point `BMF-006`.

It extends the already certified `BMF-005` zero-resource sovereign boot contract.

It does not change MAESTRO authority, install resources, discover providers, execute tools, or request network access.

## SDI-01 — Core readiness is independent from intelligence completeness

`READY` describes the health of the sovereign MAESTRO control plane.

`READY` SHALL NOT imply that every optional intelligence capability is available.

## SDI-02 — Degraded intelligence is not degraded sovereignty

When no intelligence resource is available, MAESTRO MAY remain fully sovereign and operational while reporting degraded intelligence capability.

```text
CORE_READY
    !=
FULL_INTELLIGENCE

DEGRADED_INTELLIGENCE
    !=
DEGRADED_CORE
```

## SDI-03 — Zero-resource state is explicit

When no usable intelligence resource exists, the Genesis report SHALL expose an explicit intelligence state rather than silently presenting capability absence as full availability.

The certified zero-resource state is `SOVEREIGN_DEGRADED`.

## SDI-04 — Deterministic governance remains active

Zero-resource degraded intelligence SHALL preserve deterministic governance, recovery, registry, kernel, Council, evidence, and authority boundaries.

The intelligence level for the zero-resource state is `DETERMINISTIC_ONLY`.

## SDI-05 — Resource availability is observable

The Genesis report SHALL expose the number of registered intelligence resources and the number of currently available intelligence resources.

UNKNOWN SHALL NOT be silently converted to available.

## SDI-06 — Capability availability is observable

The Genesis report SHALL explicitly expose available intelligence capabilities and unavailable intelligence capabilities.

The capability vocabulary SHALL derive from the generic MAESTRO intelligence capability contract rather than from a particular provider or model family.

## SDI-07 — Existing sovereign degraded-mode logic is authoritative for capability assessment

Genesis SHALL reuse the existing sovereign `DegradedModeController` and `IntelligenceResourceRegistry` rather than create a competing degraded-mode mechanism.

Reporting SHALL reflect the governed sovereign registry state.

## SDI-08 — No implicit acquisition

A degraded intelligence report SHALL NOT trigger installation, download, discovery, activation, provider selection, network access, external process creation, or tool execution.

```text
REPORT UNAVAILABLE
    !=
ACQUIRE RESOURCE
```

## SDI-09 — No authority expansion

Intelligence-state reporting grants no authorization, AY verdict, EX authorization, promotion authority, activation authority, execution authority, or system truth.

Observation and reporting remain non-authoritative.

## SDI-10 — Technology-time independence

The degraded intelligence contract SHALL remain independent of any contemporary provider, model family, runtime, accelerator, hardware class, or protocol.

Known technologies are adapter data, not constitutional identity.

## BordingMap boundary

```text
BMF-005 = Sovereign Core can boot with zero intelligence resources.

BMF-006 = Sovereign Core remains operational and explicitly reports
          intelligence-resource and capability unavailability.
```

BMF-006 does not authorize resource discovery, acquisition, installation, routing, execution, promotion, or activation.

## Certified zero-resource report shape

```text
status: READY

intelligence:
    state: SOVEREIGN_DEGRADED
    level: DETERMINISTIC_ONLY
    registered_resources: 0
    available_resources: 0
    available_capabilities: []
    unavailable_capabilities: [...]
    reason: explicit explanation
```

## Evidence requirements

A checkpoint claiming BMF-006 conformance must demonstrate at least:

1. Core status remains `READY` with zero intelligence resources;
2. intelligence state is explicitly `SOVEREIGN_DEGRADED`;
3. intelligence level is `DETERMINISTIC_ONLY`;
4. registered and available resource counts are explicit;
5. available and unavailable capability sets are explicit;
6. unavailable capabilities derive from the generic capability contract;
7. existing sovereign degraded-mode assessment is reused;
8. zero-resource boot performs no network request;
9. zero-resource boot launches no external process;
10. no authority is expanded by the report;
11. BordingMap point `BMF-006` is assessed with evidence.

## Final invariant

> MAESTRO may have zero external intelligence resources and still remain a healthy sovereign system.

Intelligence resources extend MAESTRO reach.

They do not define MAESTRO existence, sovereignty, or authority.
