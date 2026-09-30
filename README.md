# MAESTRO

> **Sovereign, evidence-governed control plane for artificial intelligence.**

**MAESTRO COMMANDS MODELS. MODELS DO NOT COMMAND MAESTRO.**

MAESTRO is an open engineering project created to explore a different architecture for artificial intelligence systems: models provide intelligence, while routing, authority, validation, evidence, memory, policy evolution and durable state remain governed by a sovereign control plane.

- Website: **https://maestro.men**
- Official source: **https://github.com/eddarsglobal/maestro**
- Contact: **maestro.men@gmail.com**
- Current public core: **MAESTRO v1.1.0 R1**
- Python: **3.11+** (certified environment: Python 3.12)
- Local AI runtime verified with: **Ollama**
- Community license: **GNU AGPL-3.0-or-later**
- Commercial licensing: **available from EddarsGlobal**

---

## Table of contents

1. [What is MAESTRO?](#what-is-maestro)
2. [Why MAESTRO exists](#why-maestro-exists)
3. [Core principles](#core-principles)
4. [Architecture](#architecture)
5. [Current capabilities](#current-capabilities)
6. [The 18 Councils](#the-18-councils)
7. [Requirements](#requirements)
8. [Quick installation](#quick-installation)
9. [Run the full regression suite](#run-the-full-regression-suite)
10. [Boot MAESTRO](#boot-maestro)
11. [Connect local AI with Ollama](#connect-local-ai-with-ollama)
12. [Examples](#examples)
13. [Repository structure](#repository-structure)
14. [Local-first philosophy](#local-first-philosophy)
15. [maestro.men](#maestromen)
16. [Contributing](#contributing)
17. [Commercial licensing](#commercial-licensing)
18. [Creator and stewardship](#creator-and-stewardship)
19. [Security](#security)
20. [Roadmap](#roadmap)

---

## What is MAESTRO?

MAESTRO is not intended to be only a chatbot, a model wrapper, or a conventional multi-agent conversation framework.

MAESTRO is designed as an **AI control plane**.

Its purpose is to coordinate intelligence resources while preserving explicit control over:

- task lifecycle;
- authority boundaries;
- Council responsibilities;
- model and provider selection;
- cognitive budgets;
- evidence collection;
- independent validation;
- durable memory;
- outcome attribution;
- adaptive policy proposals;
- governed activation;
- canary verification;
- rollback;
- recovery;
- traceability.

A simplified view:

```text
USER / APPLICATION
        |
        v
+---------------------+
|       MAESTRO       |
|  Sovereign Control  |
|        Plane        |
+----------+----------+
           |
   +-------+-------+
   |       |       |
   v       v       v
Councils Evidence Memory
   |       |       |
   +-------+-------+
           |
           v
 Sovereign Intelligence
           |
   +-------+--------+----------------+
   |                |                |
   v                v                v
 Ollama         LM Studio        Other providers
   |
   v
 Local models
```

The architectural rule is simple:

> **Models can recommend, reason, generate and evaluate.  
> Models do not own MAESTRO's authority.**

---

## Why MAESTRO exists

Modern AI systems are powerful, but model intelligence and system authority are often mixed together.

A model may be asked to:

- decide what to do;
- decide which tool to use;
- decide whether the work is complete;
- judge its own output;
- update memory;
- choose the next agent;
- change system behavior.

MAESTRO explores a different separation of concerns.

```text
MODEL
= intelligence resource

MAESTRO
= authority + orchestration + governance + verification
```

The goal is not to make models weaker.

The goal is to make the system around them more explicit, inspectable, replaceable and governable.

---

## Core principles

### 1. MAESTRO commands models

```text
MAESTRO COMMANDS MODELS.
MODELS DO NOT COMMAND MAESTRO.
```

### 2. MAESTRO size is not model size

A larger model does not automatically imply a better MAESTRO system.

### 3. Scale by reach, not mass

```text
MAESTRO SHALL SCALE BY ADDING REACH, NOT MASS.
```

MAESTRO should activate only the resources needed for the current mission.

### 4. Default state should be almost empty

Dormant Councils and unused context should remain unloaded whenever possible.

### 5. Models collaborate only through MAESTRO

Cross-model collaboration must remain visible to the control plane.

### 6. Evidence is stronger than self-report

An executor saying "done" is not equivalent to verified completion.

### 7. Outcomes may inform adaptation, but may not authorize it

Learning evidence can produce candidates. Governance decides whether a policy becomes active.

---

## Architecture

The intended MAESTRO lifecycle is:

```text
HEAR
  |
UNDERSTAND
  |
FRAME
  |
DECIDE OPERATING MODE
  |
CONTRACT
  |
CONDUCT
  |
VERIFY
  |
SYNTHESIZE
  |
REMEMBER
```

MAESTRO also supports operating-mode concepts ranging from direct work to larger governed missions:

```text
M0_DIRECT
M1_SPECIALIST
M2_STRIKE_TEAM
M3_MISSION
M4_GENERAL_COUNCIL
M5_CRISIS
```

The control plane is deterministic where authority, state transitions, persistence and transaction integrity are concerned.

Models contribute intelligence inside those boundaries.

---

## Current capabilities

MAESTRO v1.1.0 R1 currently includes substantial infrastructure in the following areas:

| Area | Current capability |
| --- | --- |
| Production boot | `ProductionGenesisSystem` |
| Councils | 18 Genesis Councils |
| Mission lifecycle | Governed state machine |
| Orchestration | DAG and dispatch infrastructure |
| Local AI | Ollama provider and discovery |
| Sovereign intelligence | Registry, router, fallback, degraded mode |
| Model economics | Cognitive Economy |
| Model/resource selection | Intelligence Market |
| Multi-resource reasoning | Cognitive Fabric |
| Meta-level control | Meta Cognition |
| Evidence | Evidence store and verification flows |
| Learning | Experience and learning infrastructure |
| Academy | Replay, benchmarks, scoring, evaluation |
| Outcome analysis | Outcome Intelligence |
| Adaptation | Outcome-Governed Adaptation |
| Runtime policy changes | Governed Policy Activation |
| Persistence | Durable state and ledgers |
| Recovery | Runtime recovery paths |
| Transaction integrity | Content-addressed, hash-chained runtime events |
| Resilience | Fabric, cluster and recovery components |
| Tools | Tool registry |
| Telemetry | Tracing infrastructure |

### Certified R1 baseline

The current R1 distribution was validated with:

```text
MAESTRO version: 1.1.0
Regression suite: 283 / 283 tests
ProductionGenesis: READY
Real local inference path: VERIFIED
```

The certified development environment used Python 3.12.

---

## The 18 Councils

MAESTRO Councils are not merely fictional personas.

A Council represents a governed domain with responsibilities, boundaries and expected evidence.

All public Council blueprints are available in [`blueprints/`](./blueprints/).

| Council | Primary domain | Blueprint |
| --- | --- | --- |
| EX | Direction, routing and mission lifecycle | [Council EX](./blueprints/Council-ex.md) |
| AY | Acceptance contracts and final validation | [Council AY](./blueprints/Council-ay.md) |
| IT | Technology, implementation and code | [Council IT](./blueprints/Council-it.md) |
| JR | Legal and compliance interpretation | [Council JR](./blueprints/Council-jr.md) |
| MK | Market and marketing strategy | [Council MK](./blueprints/Council-mk.md) |
| CM | Creation, content and media | [Council CM](./blueprints/Council-cm.md) |
| OP | Operations, releases and recovery | [Council OP](./blueprints/Council-op.md) |
| FN | Financial analysis and constraints | [Council FN](./blueprints/Council-fn.md) |
| AD | Administrative and jurisdictional domain | [Council AD](./blueprints/Council-ad.md) |
| DA | Design quality and visual/product design | [Council DA](./blueprints/Council-da.md) |
| PM | Product scope and product management | [Council PM](./blueprints/Council-pm.md) |
| CS | User success and user-facing experience | [Council CS](./blueprints/Council-cs.md) |
| DT | Telemetry, measurement and data truth | [Council DT](./blueprints/Council-dt.md) |
| SC | Security architecture and independent audit | [Council SC](./blueprints/Council-sc.md) |
| TX | Traceability, durable state and documentation | [Council TX](./blueprints/Council-tx.md) |
| PR | Performance and real-world evidence | [Council PR](./blueprints/Council-pr.md) |
| AI | AI/ML architecture, evaluation and model policy | [Council AI](./blueprints/Council-ai.md) |
| RX | External research and evidence gathering | [Council RX](./blueprints/Council-rx.md) |

For the Council registry and liaison model, see:

- [APTE Council Registry and Liaison Contract](./blueprints/APTE_COUNCIL_REGISTRY_AND_LIAISON_CONTRACT.md)
- [Councils overview](./docs/COUNCILS.md)

---

## Requirements

### Required

- Git
- Python **3.11 or newer**
- `pip`
- a terminal

### Recommended

- Python **3.12**
- a Python virtual environment
- Ollama for local model execution

### Optional

Depending on the capabilities you want to use:

- additional local model runtimes;
- external providers;
- development tools;
- editor/IDE;
- GitHub Desktop.

---

## Quick installation

### 1. Clone the repository

```bash
git clone https://github.com/eddarsglobal/maestro.git
cd maestro
```

### 2. Verify Python

```bash
python3 --version
```

MAESTRO requires:

```text
Python >= 3.11
```

Python 3.12 is recommended.

If `python3.12` is available:

```bash
python3.12 --version
```

### 3. Create a virtual environment

```bash
python3.12 -m venv .venv
```

If your Python executable has another path, use that path explicitly.

Example on some macOS installations:

```bash
/usr/local/bin/python3.12 -m venv .venv
```

### 4. Always use the virtual environment's Python directly

Check it:

```bash
./.venv/bin/python --version
```

This avoids shell aliases accidentally invoking a different Python version.

### 5. Upgrade packaging tools

```bash
./.venv/bin/python -m pip install --upgrade pip setuptools wheel
```

### 6. Install MAESTRO

For development:

```bash
./.venv/bin/python -m pip install -e .
```

For a standard local installation:

```bash
./.venv/bin/python -m pip install .
```

A successful v1.1.0 installation installs:

```text
maestro-core 1.1.0
```

For a more detailed guide, see [docs/INSTALLATION.md](./docs/INSTALLATION.md).

---

## Run the full regression suite

Before experimenting with the core, validate your checkout:

```bash
./.venv/bin/python -m unittest discover -s tests -q
```

For the v1.1.0 R1 baseline, the expected result is:

```text
----------------------------------------------------------------------
Ran 283 tests
OK
```

If the test count changes in a later development branch, refer to the release notes for that branch.

---

## Boot MAESTRO

Create a local runtime directory by booting `ProductionGenesisSystem`:

```bash
./.venv/bin/python - <<'PY'
from pathlib import Path
from maestro import ProductionGenesisSystem

system = ProductionGenesisSystem(Path("runtime"))
result = system.start()

print("=" * 72)
print("MAESTRO")
print("=" * 72)
print("VERSION :", result["version"])
print("STATUS  :", result["status"])
print("BOOT    :", result["boot"])
print("RECOVERY:", result["recovery"])
PY
```

Expected v1.1.0 status:

```text
VERSION : 1.1.0
STATUS  : READY
```

The repository `.gitignore` excludes the mutable root runtime directory from source control.

---

## Connect local AI with Ollama

MAESTRO has a verified local provider path for Ollama.

### 1. Install Ollama

Install Ollama using the official distribution for your operating system.

### 2. Verify the service

```bash
ollama --version
```

Check the local API:

```bash
curl -fsS http://127.0.0.1:11434/api/tags
```

### 3. Install a model

Example:

```bash
ollama pull qwen3:8b
```

or a coding model:

```bash
ollama pull qwen3-coder
```

### 4. List installed models

```bash
ollama list
```

### 5. MAESTRO model philosophy

MAESTRO should not require the user to hard-code one model everywhere.

The long-term routing model is capability-first:

```text
task
  |
required capability
  |
MAESTRO resource selection
  |
provider
  |
model
```

The local provider implementation is under:

```text
src/maestro/providers/ollama/
```

The sovereign intelligence layer is under:

```text
src/maestro/sovereign/
```

---

## Examples

The [`examples/`](./examples/) directory includes examples for multiple generations of MAESTRO infrastructure, including:

- mission orchestration;
- learning;
- Academy;
- adaptive behavior;
- autonomous runtime;
- operating system;
- distributed fabric;
- resilient cluster;
- local intelligence;
- sovereign intelligence;
- Intelligence Market;
- Cognitive Fabric;
- Cognitive Economy;
- Meta Cognition;
- Strategic Adaptation;
- Production Genesis.

Start with:

```bash
./.venv/bin/python examples/v10_production_genesis_demo.py
```

Then explore the other examples according to the subsystem you are studying.

---

## Repository structure

```text
maestro/
├── src/
│   └── maestro/
│       ├── academy/
│       ├── adaptive/
│       ├── autonomous/
│       ├── cognitive_economy/
│       ├── cognitive_fabric/
│       ├── councils/
│       ├── evidence/
│       ├── fabric/
│       ├── genesis/
│       ├── governance/
│       ├── governed_activation/
│       ├── intelligence_market/
│       ├── learning/
│       ├── memory/
│       ├── meta_cognition/
│       ├── orchestration/
│       ├── os/
│       ├── outcome_governed_adaptation/
│       ├── outcome_intelligence/
│       ├── providers/
│       ├── resilience/
│       ├── sovereign/
│       ├── storage/
│       ├── strategic_adaptation/
│       ├── telemetry/
│       └── tools/
│
├── tests/
├── docs/
├── examples/
├── blueprints/
├── config/
├── .github/
├── README.md
├── LICENSE
├── COMMERCIAL_LICENSE.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── GOVERNANCE.md
├── ROADMAP.md
├── TRADEMARKS.md
├── CHANGELOG.md
└── pyproject.toml
```

---

## Local-first philosophy

MAESTRO is being developed around a local-first architecture whenever practical.

The planned `maestro.men` user interface is designed to work as a lightweight web interface while the user's MAESTRO runtime, conversations, local models, memory and execution can remain on the user's own machine.

Conceptually:

```text
maestro.men
    |
    | user interface
    v
MAESTRO Local Gateway
    |
    v
MAESTRO Core
    |
    +-- local models
    +-- tools
    +-- memory
    +-- evidence
```

A future user should be able to connect local intelligence providers from Settings without giving the web frontend ownership of the local models.

---

## maestro.men

**maestro.men** is the planned official user-facing interface for MAESTRO.

The design direction includes:

- mobile-first interface;
- dark / light / system themes;
- English, German, French, Arabic, Portuguese, Spanish, Croatian and Italian;
- local conversation storage;
- pinned conversations;
- rename, share, export and delete;
- recent chats;
- local provider configuration;
- local model discovery;
- advanced mission view;
- Council visibility;
- links to Council blueprints;
- GitHub developer resources;
- elegant Markdown help;
- open-source contribution links.

The web UI and the MAESTRO control plane are separate layers.

---

## Contributing

MAESTRO is open to engineers, researchers and builders around the world.

We welcome contributions related to:

- architecture;
- model/provider adapters;
- Councils;
- routing;
- evaluation;
- evidence;
- local AI;
- performance;
- security;
- testing;
- documentation;
- UI integration;
- Local Gateway;
- developer tooling.

Before contributing, read:

- [CONTRIBUTING.md](./CONTRIBUTING.md)
- [GOVERNANCE.md](./GOVERNANCE.md)
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)
- [SECURITY.md](./SECURITY.md)

Please open an Issue before beginning a large architectural change.

---

## Commercial licensing

The community version of MAESTRO is distributed under the **GNU Affero General Public License v3.0 or later**.

Organizations may use MAESTRO under the terms of that license.

EddarsGlobal also offers separate commercial licensing for organizations that require, for example:

- proprietary or closed-source integration;
- licensing terms different from AGPL;
- enterprise deployment arrangements;
- commercial support;
- custom integration;
- professional implementation;
- private development;
- contractual support terms.

For commercial licensing and enterprise cooperation:

**Nourddine Eddars — EddarsGlobal**  
**maestro.men@gmail.com**

See [COMMERCIAL_LICENSE.md](./COMMERCIAL_LICENSE.md).

---

## Creator and stewardship

MAESTRO was created by **Nourddine Eddars**, founder of **EddarsGlobal**, a Swiss creator and entrepreneur of Moroccan Arab heritage.

The project began as an independent effort to explore a sovereign architecture for artificial intelligence systems in which models provide intelligence but do not own the system's authority.

MAESTRO is created and stewarded by **EddarsGlobal**.

Community contributions are welcomed and are intended to strengthen the official open development of the project.

Official website:

**https://maestro.men**

Contact:

**maestro.men@gmail.com**

---

## Security

Please do not publish security vulnerabilities as public Issues.

See:

[SECURITY.md](./SECURITY.md)

Security contact:

**maestro.men@gmail.com**

---

## Roadmap

The next major product direction includes:

1. MAESTRO Local Gateway;
2. `maestro.men` user interface;
3. local-first chat and settings;
4. richer provider abstraction;
5. model/resource management;
6. Council and evidence visualization;
7. GitHub-linked developer documentation;
8. safer tool execution;
9. broader platform support;
10. community contribution infrastructure.

See [ROADMAP.md](./ROADMAP.md).

---

## License

Community use is governed by the GNU Affero General Public License v3.0 or later.

Commercial licensing is available separately from EddarsGlobal.

See:

- [LICENSE](./LICENSE)
- [COMMERCIAL_LICENSE.md](./COMMERCIAL_LICENSE.md)
- [TRADEMARKS.md](./TRADEMARKS.md)

---

## Final principle

> **MAESTRO COMMANDS MODELS. MODELS DO NOT COMMAND MAESTRO.**

MAESTRO is an evolving open engineering project.

Its goal is not to make one model the center of the system.

Its goal is to make intelligence **replaceable, governable, verifiable and useful**.
