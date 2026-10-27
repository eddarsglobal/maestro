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


## UDP 2.1.0 x 18 Councils — anti-duplication and Guardian-gated integration (27 Oct 2026)

**Status:** PROPOSED / IMPLEMENTATION NOT CERTIFIED. The existing G0 -> G1 -> G2 -> G3 hard gates and \`PRODUCTION RELEASE: BLOCKED\` remain unchanged. This section records an owner-requested design and evidence gates; it does not assert deployment or model/semantic correctness. It applies to the coordinated repositories \`maestro\`, \`maestro-gateway\`, and \`maestro-ui\`, with the installed Mac sources to be reconciled before any functional patch.

### Constitutional invariants — never waive

- **INSPECT BEFORE CREATE:** inspect current Mac sources, tracked source history, tests, configs, current model policy, Gateway, Core and UI, and existing Guardian implementations first. Record a file/symbol/behavior-level inventory with source hashes. No new file, Council, agent, router, model-manager, record format, approval mechanism, UI or testing infrastructure unless proven absent and strictly necessary. Reuse, repair, restore, extend or reorganize existing components. A GitHub snapshot alone is not proof of the installed Mac source.
- **18 EXISTING COUNCILS ONLY:** preserve their identities, \`CouncilSpec\` responsibilities, \`cannot_own\` constraints and APTE liaison contract; \`EX\` alone routes, domain Councils work/audit their domain, \`AY\` alone gives SYSTEM acceptance, \`OP\` owns release/retry controls, \`TX\` owns durable traceability and \`RX\` supplies external evidence through EX. Never fabricate separate Council participation, expertise or independence.
- **UDP v2.1.0 IS A PROTOCOL, NOT NINE NEW AGENTS:** map its Governor/Investigator/Constructor/Critic/User Advocate/Specialist/Verifier/Guardian/Orchestrator *functions* onto existing authorized Council functions and deterministic checks. Preserve actual permissions and APTE authority; UDP Markdown cannot grant access, authorize mutation or certify its own deployment.
- **USER CHOICE SUPREME / ZERO-MODEL CORE:** user-selected compatible local conversational model takes precedence over recommendations. Qwen3.5-2B is optional first-run advice, not a Core dependency or forced download; no silent model swap; no cloud default. Keep the existing neutral engine discovery and model refresh. One primary conversational model by default.
- **ATOMIC RESPONSIVENESS:** \`DIRECT\` chat must not convene 18 Councils, perform nine invented debates, or add unrequested LLM calls. A selected Council is not an executed Council. UDP effort is risk-proportional and is benchmarked on real CPU hardware, alongside output quality in EN/FR/DE/AR/PT/ES/HR/IT.
- **TRUTH SCOPES:** keep \`DOMAIN JUSTE/FAUTE\`, \`AY SYSTEM JUSTE/FAUTE\`, TX/EX commit boundaries and release gates. Map UDP \`PASS/FAIL/NOT_RUN/INCONCLUSIVE/NOT_APPLICABLE\` and overall \`PASS/PASS_WITH_CONTROLS/REMEDIATE/BLOCK/UNVERIFIED/INCONCLUSIVE\` without falsely equating delivery integrity to semantic/factual correctness. Record *all* unresolved findings.

### Sequential execution checkpoints — Guardian checks each item separately

- [ ] **UDP21-C18-00 | Establish exact installed baseline.** Verify FIX3 outcome (pending), clean/dirty Mac tree, SHA-256 for the three repos, current 18-Council registry/APTE contracts, model choice, actual Gateway call graph and extant local consolidated Guardian. Resolve GitHub-vs-Mac drift *before* proposing code changes. **Guardian evidence:** source hashes, file/symbol inventory, integration map, known blockers. **Gate:** BLOCK when installed baseline is unknown or incompatible.
- [ ] **UDP21-C18-01 | Duplicate-prevention matrix.** Inspect and enumerate \`COUNCILS\`, \`GovernedMissionFoundation.analyze/synthesize_council_graph\`, \`Dispatcher\`, \`DagEngine\`, context compiler, ActionFirewall, AY verdict, EvidenceStore, response guard, budget governor and model refresh. For each UDP requirement classify \`EXISTS_AND_USED\`, \`EXISTS_NOT_WIRED\`, \`NEEDS_CORRECTION\`, or \`PROVEN_MISSING\`, with actual file references. **Guardian evidence:** function-to-function mapping and explicit negative duplicate scan. **Gate:** BLOCK new equivalent abstractions or Council clones.
- [ ] **UDP21-C18-02 | Real role-based mission wiring.** Extend the *existing* mission path and graph/dispatch facilities so EX can engage exactly the Council domains demanded by the real task. Preserve minimal \`EX -> AI -> AY -> TX\` for ordinary chat and \`EX -> RX -> AY -> TX\` where applicable; only add domain branches with documented triggers and actual work. Do not count static names, intent keywords, fake verdicts, or a routing record as an executed Council task. **Guardian evidence:** real runnable mission traces for IT, SC, PR, JR, FN and a cross-domain case, with negative routing cases and authorization tests. **Gate:** REMEDIATE if routing exists only cosmetically; BLOCK any unauthorized dispatch.
- [ ] **UDP21-C18-03 | Proportionate UDP operation.** Reuse the existing task classifier, Core governance and response guards to implement/associate UDP \`DIRECT\`, \`STANDARD\`, \`CRITICAL\`, \`EXPLORATORY\`, \`INCIDENT\`, \`REVIEW\` as *deliberation policy*, not a conflicting replacement for \`M0_DIRECT\` technical execution mode. Risk escalation, role functions, counterchecks and source/claim classification must be task-scoped. \`REVIEW\` must audit an existing output without falsely claiming independent external checks. **Guardian evidence:** representative real/fixture tasks per mode, permissions and latency deltas. **Gate:** BLOCK invented independence or hidden extra inference on routine requests.
- [ ] **UDP21-C18-04 | Evidence and acceptance truthfulness.** Keep existing mission evidence, Council DOMAIN verdicts and AY SYSTEM verdict. Distinguish \`DEFINED\`, \`SELECTED\`, \`EXECUTED\`, \`VERIFIED\`; only surface participation backed by observed execution. Use UDP epistemic and check-state labels without claiming a JSON record alone proves facts. Preserve all defects, uncertainties, evidence provenance and \`NOT_RUN\` checks; do not upgrade delivery-only AY verdicts to semantic certification. **Guardian evidence:** injected failures, absent proofs, stale versions, contradicted claims, rollbacks and scope-specific verdicts. **Gate:** BLOCK fabricated execution, evidence, or blanket \`CERTIFIED\` claims.
- [ ] **UDP21-C18-05 | Quality, latency, multilingual regressions.** Compare before/after on the *same* user machine/model/prompt/task, measuring first-token, end-to-end latency, actual model calls, CPU/memory and eight-language naturalness and permission accuracy. No compulsory additional model calls for \`DIRECT\`. Check real Ollama alternative provider, existing model choice/first-run behavior, zero-model boot and authorized side-effect guards. **Guardian evidence:** Core/Gateway/UI automated tests + human-reviewed real mission receipts; test oracle and observed/untested separation. **Gate:** REMEDIATE any meaningful performance or language regression; do not infer universal improvements from stub tests.
- [ ] **UDP21-C18-06 | Reconcile, review and release gate.** Run scoped static tests, full Core/Gateway regression, UI build, negative security tests, rollback and actual end-user scenarios. Guardian inspects each checkpoint separately and refuses sequential progression if its prerequisite is BLOCK/REMEDIATE/UNVERIFIED. Coordinate three repos without overwriting unrelated commits; publish reviewed branch/PR, not unreviewed main pushes. Existing G1 P0, G2 real linguistic and G3 platform/release gates retain authority. **Guardian evidence:** full versioned logs, commit IDs, CI, live receipts, qualified review where necessary. **Release:** BLOCKED until the real preexisting release authority approves.

### Existing Guardian — mandatory check-by-check directive

- Reuse \`agents/Roadmap_guardian.py\` as the existing tri-repo source-control preflight; **do not pretend that adapter runs G0-G3, watches the Mac continuously, or is an autonomous AI Guardian**. Reuse the existing consolidated Guardian for full test/release authority when available and verified.
- Before each \`UDP21-C18-XX\` checkpoint, obtain actual evidence matching the exact installed revision and scope. Produce \`PASS\`, \`REMEDIATE\`, \`BLOCK\`, \`UNVERIFIED\` or \`INCONCLUSIVE\` with a reason, file/line/receipt references, responsible Council, next authorized check and unresolved findings. **No checked box without actual acceptance evidence.**
- Prevent moving to the next checkpoint on \`BLOCK\` or \`REMEDIATE\`, and do not mark a required check \`PASS\` when proof is \`NOT_RUN\`; request independent human authorization for release conditions outside Guardian's remit.
- The prior provisional \`MAESTRO_UDP21_COUNCILS_INTEGRATION\` mission patch is **not an authorized installation**. Its model-free keyword-classification tests and static Council references do not demonstrate Council-domain execution, integration with the existing mission graph, or full UDP conformance. Reassess under C00/C01 before reuse; discard redundant code.
- This roadmap instructs the existing Guardian workflows when invoked by a developer/CI/authorized owner. **It is not proof that any daemon or background monitoring was started.**

**Current evidence verdict for these checkpoints:** C00–C06 \`NOT_RUN / BLOCKED FOR INSTALLATION\`; no source patch or UDP runtime implementation is certified here. The previous Mac FIX3 result has not yet been supplied. UDP specification itself is \`SPECIFICATION_DRAFT / NOT_BENCHMARKED / NOT_CERTIFIED\`.
