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

## Official tri-repository source-control contract (V8.1 reconciliation)

- Official local roots: `/Users/noury/Documents/App_py/MAESTRO_AGENT/Github/maestro`,
  `/Users/noury/Documents/App_py/MAESTRO_AGENT/Github/maestro-gateway`,
  `/Users/noury/Documents/App_py/MAESTRO_AGENT/Github/maestro-ui`.
- Official GitHub repositories: `eddarsglobal/maestro`, `eddarsglobal/maestro-gateway`,
  `eddarsglobal/maestro-ui`. This document is installed separately in each repository.
- V8.1 source ZIP SHA-256: `446a9fcbbd5d96773e119e3733d919141f86ec9e1430c9e3030cc7bf49fc7503`.
- Baseline source commits: `maestro=c8f425af1f50810b9cbf8dc779d4c642ceea2215`;
  `maestro-gateway=0e35e8056e774ab5ba89c7b2b58d9f83ec53ed78`;
  `maestro-ui=dd15753e8110ef4b7f798a11cf85caad0d435b53`.
- **Source of truth**: each official Git repository and its reviewed commits. ZIPs are
  immutable delivery snapshots, not a substitute for Git history.
- Maintain coordinated tri-repo commit provenance for each reviewed integration.
  Do not overwrite independent LICENSE, CI, governance or documentation files.
- Guardian rules: verify the three repo identities, clean source history,
  integrated regressions, reviews, GitHub CI, and release evidence. Never mark a
  gate PASS merely because a ZIP test passed. Do not auto-push or force-push.
- The legacy consolidated-package Guardian remains the G0/G1/G2/G3 test gate.
  The repo-local Guardian adapter only checks source-control identity; it does
  **not** replace the consolidated certification tests.
- Local-first: English is the default among EN/FR/DE/AR/PT/ES/HR/IT; retain
  one active conversational LLM, provider neutrality, no automatic cloud-primary
  inference or model downloads, and no semantic claims from tiny probes.
- **Release status: BLOCKED**. G1 full P0 closure, G2 semantic language review
  and G3 notarized macOS distribution are not certified by this integration.
