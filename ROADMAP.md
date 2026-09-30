# MAESTRO Roadmap

This roadmap describes intended directions and is not a guarantee of delivery dates.

## Current baseline

### MAESTRO v1.1.0 R1

Current verified foundations include:

- Production Genesis;
- 18 Councils;
- orchestration DAG;
- Evidence infrastructure;
- Local Intelligence;
- Sovereign Intelligence;
- Intelligence Market;
- Cognitive Fabric;
- Cognitive Economy;
- Meta Cognition;
- Strategic Adaptation;
- Outcome Intelligence;
- Outcome-Governed Adaptation;
- Governed Policy Activation;
- durable runtime state;
- transaction recovery;
- hash-chained transaction integrity;
- Ollama local inference path.

## Next product layer

### MAESTRO Local Gateway

Build the secure local interface between:

```text
maestro.men
     |
browser
     |
127.0.0.1
     |
MAESTRO Local Gateway
     |
MAESTRO Core
```

Priorities include:

- loopback-only binding by default;
- origin controls;
- pairing;
- local session authorization;
- health endpoint;
- provider discovery;
- model discovery;
- mission submission;
- streaming mission events;
- conversation persistence;
- evidence access;
- Council state visibility.

## maestro.men

Planned web UI:

- mobile-first;
- ChatGPT/Claude/DeepSeek-class interaction simplicity;
- MAESTRO-specific visual identity;
- dark/light/system themes;
- EN/DE/FR/AR/PT/ES/HR/IT;
- local chat persistence;
- new chat;
- recents;
- pin;
- rename;
- share/export;
- delete;
- local providers;
- automatic model/resource routing;
- advanced mission view;
- Council view;
- evidence view;
- GitHub documentation links;
- elegant Markdown help.

## Open engineering priorities

- provider SDK;
- more local runtimes;
- stable Local Gateway protocol;
- stronger security review;
- richer evidence adapters;
- developer documentation;
- packaging for macOS/Windows/Linux;
- improved observability;
- reproducible release tooling;
- contribution governance;
- enterprise integration paths.

## Long-term direction

MAESTRO should remain model-independent.

The project should be able to use new intelligence providers without surrendering control-plane authority to them.
