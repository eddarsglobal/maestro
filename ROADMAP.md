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

### UDP21-C18-00 — Mac field evidence received 2026-10-27 (checkpoint OPEN)

**Evidence origin:** owner-provided read-only Terminal output, not an independent source-file inspection, not a CI run, not a real Gateway mission and not an authorized Guardian certification.

- Installed local branch across all three repositories: `dev/checkpoint-v8115-g1p0a1`; HEADs `maestro=e46ef5a7e8576b758290c0b5f6f5309449d479e1`, `maestro-gateway=febde93f7eaad59d836e98a351f7cd428be50ff1`, `maestro-ui=890a03e70f7f3d6ae1e424deb65a972b49930596`. All working trees reported **DIRTY/UNKNOWN**. Do not replace, reset, stage, commit or push these uncommitted sources as part of this roadmap review.
- Installed FIX3 first-run model-choice receipt reported `INSTALLED_TECHNICAL_ONLY_RESTART_PENDING`, `guardian=G1_REMEDIATE`, `functional_live=NOT_TESTED`, `release_authorized=false`, `models_downloaded=0`. The owner's grep of the install log reports `CORE_UNITTEST_PASSED=1426` and `GATEWAY_UNITTEST_PASSED=862`; the entire test logs, UI build and live post-restart user scenario have not been independently examined here.
- Owner-reported SHA-256: `maestro-gateway/src/maestro_gateway/mission.py=c620a76348067536f90cb258fa33be21655ad30214775a38c8fc1cfbbd3a29ff`; `server.py=ace552acccd08e7b0a27587328dc19fb627dee0a07998397771aaa5e7cf1e942`; `maestro-ui/src/App.tsx=67a24d1a194cd7172a349852987722ceb668d90f312a338031de6dcb61ed7b84`.
- **Previously unseen local changes exist**, including `semantic_verifier.py`, `symbolic_task_prover.py`, `sovereign_evidence_ledger.py`, `delivery_contracts.py`, `response_effort.py`, `response_constraints.py`, `language_quality_governor.py`, `native_linguistic_revision.py`, `cooperative_admission.py`, `effect_journal.py`, and additional regressions. File presence and Git dirty status DO NOT establish their runtime behavior, integrity, or effect.
- **Guardian action required:** inspect these exact local files and their call sites, search for the same UDP/Council mechanisms before any new development, reconcile the FIX3 live Gateway restart/use with source-revision receipts, and verify full scoped regressions without overwriting working changes. Do not install the earlier provisional UDP mission patch.
- **Scoped gate:** C00 `UNVERIFIED` (partial evidence only); C01 `NOT_RUN` (read-only inspection permitted but no implementation), C02-C06 `BLOCKED`. Existing G1/G2/G3 release gates remain blocked. No new Council, Guardian, router, model-discovery system, or UDP parallel engine is authorized by this record.


### UDP21-C18-01 — Mac symbol and reference inventory received 2026-10-27 (NOT_YET_VALIDATED)

**Evidence:** owner-provided output of a read-only AST/source-text inspection of current local Mac working trees, not a live capability execution and not proof of network-independent reviewers. All paths below refer to \`maestro-gateway/src/maestro_gateway/\`, except the named Core symbols.

- Inspected **16 existing Gateway modules**, all present and parseable: \`semantic_verifier\`, \`symbolic_task_prover\`, \`sovereign_evidence_ledger\`, \`delivery_contracts\`, \`response_effort\`, \`response_constraints\`, \`language_quality_governor\`, \`native_linguistic_revision\`, \`cooperative_admission\`, \`native_admission\`, \`effect_journal\`, \`request_journal\`, \`language_benchmark_evidence\`, \`multilingual_mission_contract\`, \`conversation_language_context\`, and \`lossless_sentence_repair\`. Their declarations and content digests were displayed by Terminal.
- Textual references **in six selected Gateway consumers** exist for 14/16 modules, including \`mission.py\` for semantic verification, bounded response effort, language quality, linguistic revision, effect journal, request journal, prior-language context, and sentence repair; \`response_guard.py\` for delivery constraints; \`primary_intelligence.py\` for the sovereign evidence ledger and language evidence; \`server.py\` for native admission and loading benchmark evidence. **These are source references, not demonstrated runtime execution or semantic success.**
- \`symbolic_task_prover.py\` and \`cooperative_admission.py\`: \`DIRECT_REFERENCES_IN_SELECTED_CONSUMERS: NONE_FOUND\`. **NOT a finding of unused code**; check all Python modules, tests, imports and transitive invocation before claiming either unintegrated or redundant.
- Core still exposes \`COUNCILS\`, \`GovernedMissionFoundation.synthesize_council_graph\`, \`Dispatcher.dispatch\`, \`RuntimeKernel.submit_verdict\` and \`add_evidence\` as symbol matches, but **no source-proven call chain from current \`mission.py\` to graph synthesis** has yet been established. Inspect real AST call sites and Council-trigger evidence.
- Owner observed Gateway TCP listener \`PID=28425\` starting **2026-10-27 06:25:59 local**, predating FIX3 technical install receipt timestamp **2026-10-27 14:45:43**. This strongly suggests the running process predates FIX3, but not whether it has hot reload; **post-FIX3 runtime activation has NOT been verified**. Preserve running process; inspect its executable/source command first and plan any restart separately.
- **Guardian decision:** UDP21-C18-01 \`IN_PROGRESS / UNVERIFIED\`. Require cross-repository full references and function-level calls, Core-to-Gateway mission graph wiring, role-specific DOMAIN evidence, live process revision, complete logs and negatives before considering C01 closure or any C02 mutation. Existing G1/G2/G3 \`BLOCKED\`; no code or production authorization is implied.


### UDP21-C18-01 — Cross-module AST call-site evidence received 2026-10-27

**Provenance:** user-supplied read-only terminal AST search of 710 Python files under the local `maestro` and `maestro-gateway` `src/` and `tests/` directories. Parsing errors: **0**. This search is static code evidence only, not proof of executed mission behavior.

- Existing `symbolic_task_prover.prove_symbolic_task` is imported and called by `maestro-gateway/src/maestro_gateway/semantic_verifier.py` (import line 17; call line 380 in the inspected local revision), with additional tests. **Not orphaned; do not duplicate.**
- Existing `CooperativeAdmission` is imported and instantiated by `maestro-gateway/src/maestro_gateway/cross_process_foreground.py` (import line 13, constructor call line 31). **Not orphaned; do not duplicate.**
- Existing `GovernedMissionFoundation.analyze/synthesize_council_graph`, `CouncilCapabilityBinding` have 25 and 13 matched AST references respectively in the broad src+tests scan. The displayed graph call sites are tests; a full **production-src-only** caller audit is still needed to establish (or reject) real mission graph wiring.
- Exact AST expression search for `CouncilId.IT/SC/PR/FN/JR` returned **0** references in scanned src+tests; dynamic string/registry-based routing is NOT ruled out by this result. Trace Council IDs and selectors through Gateway Core request dispatch and actual mission receipts before calling these domains unreachable.
- Existing `kernel.add_evidence` and `kernel.submit_verdict` calls are present in `maestro-gateway/src/maestro_gateway/mission.py`; this establishes their call sites, **not semantic truth validation**.
- Gateway listener `PID 28425` was still displayed with a 2026-10-27 06:25:59 start timestamp, predating the FIX3 installation receipt; the Gateway restart/reload and FIX3 end-user validation are **NOT_VERIFIED**.
- **Guardian C01 finding:** parts of the earlier "possibly unused" hypothesis were falsified. **Do not create** a symbolic prover, admission coordinator, evidence ledger, specialist router or UDP Guardian before examining function-level existing implementations and their actual consumers. C01 stays `IN_PROGRESS / UNVERIFIED`; C02–C06 may not claim implementation PASS. G1/G2/G3 and production gates remain blocked.


### UDP21-C18-01 — Production-only AST inspection received 2026-10-27

**Evidence source:** owner-provided read-only AST inspection of current Mac working trees at `dev/checkpoint-v8115-g1p0a1`. No source writes; no functional missions executed.

- Core production source call sites: `maestro/src/maestro/autonomous/runtime.py:453` calls `self.kernel.start_dag_node`. The production AST matching the queried selectors did **not** show an invocation of `GovernedMissionFoundation.synthesize_council_graph` or instantiation of `CouncilCapabilityBinding`. This is negative evidence only for the particular names and scanned `src` trees; dynamic registration/call-by-alias is not excluded.
- Gateway production source `maestro-gateway/src/maestro_gateway/mission.py` has two directly visible mission-level graph paths: `mission.strike_team` at lines 884 and 1703; `kernel.route` at lines 895 and 1714; `kernel.start_dag_node` at lines 935 and 1759. The observed `CouncilId` attributes in Gateway source are **AI, AY, EX, RX, TX**, and there are no explicit `CouncilId.IT, .SC, .PR, .FN, .JR` references in Gateway source in this AST scan.
- **Duplicate-prevention directive:** `GovernedMissionFoundation`, `Dispatcher`, `DagEngine`, `CouncilCapabilityBinding`, `ActionFirewall`, the existing quality/evidence/admission modules, APTE Council registry and Guardian infrastructure must be inspected and reused. No second Council router, no duplicate Guardian, no additional Councils.
- **Gating interpretation:** specialized domain-Council execution in user-facing Gateway missions remains **UNVERIFIED**; do not label Councils 'executed' from registry or UI display alone. Before C02 code changes inspect current Mac `GovernedMissionFoundation` contract/inputs, gateway mission Core runtime, autonomous mission routing paths, actual Council binding rules, approval/evidence coupling and negative tests. Check current runtime restart/live version separately.
- **C01 checkpoint:** `IN_PROGRESS`, not a completed anti-duplication audit; C02 implementation `BLOCKED`; existing G1/G2/G3 production gates `BLOCKED`. This note is planning/evidence governance only and does not certify a source integration.


### UDP21-C18-01 — Existing interface signatures and Gateway runtime paths (2026-10-27)

**User-owned local read-only AST evidence:** Current `GovernedMissionFoundation.analyze(contract, rules)` and `synthesize_council_graph(contract, demand, bindings)` already accept `MissionContract`, `CapabilityRule` and `CouncilCapabilityBinding`. Existing `MaestroKernel.route`, `add_dag_node`, `start_dag_node` and `compile_context` remain the governed execution path. Current Gateway `mission.py` uses explicit `EX->RX->AY->TX` for governed web research and `EX->AI->AY->TX` for direct chat (local source lines approximately 884–935 and 1703–1759); no production call to the Council graph synthesizer was found by the specified AST scan. `AutonomousRuntime.run_one` uses the existing worker scheduler, `kernel.start_dag_node`, `compile_context`, and Council executor according to the accessible upstream implementation, but local adapter registrations and worker startup are **NOT_YET_INSPECTED**. Do not infer deployed multi-Council functional coverage from those interfaces.

**Guardian next discriminating check:** inspect Mac production source for `CouncilExecutor.register` / `executor.register`, `WorkerRegistry.register` / `workers.register`, `RuntimeScheduler.enqueue`, `run_one`, concrete Council-domain adapter `execute` implementations and their caller path from Gateway. Distinguish `PLANNED`, `ROUTED`, `REGISTERED`, `EXECUTED`, `EVIDENCE_RECORDED`, `AY_VERIFIED`. Preserve existing scheduler, adapter interfaces, Core/Gateway model choices, and no-extra-call DIRECT fast path. **C01 remains IN_PROGRESS/UNVERIFIED, C02 BLOCKED** until these findings are reconciled with the installed source; G1/G2/G3 remain BLOCKED.


### UDP21-C18-01 — Existing execution adapters audit received 2026-10-27

**Evidence origin:** read-only AST report provided by the owner for the current Mac source trees; 366 Python production files inspected. **Not a production-run trace.** The previously identified Core graph synthesizer still had **0 direct call sites** in that scan.

- EXISTING Council executor: `maestro/src/maestro/autonomous/runtime.py:108 CouncilExecutor()`, `runtime.py:456 self.executor.execute(...)`.
- EXISTING worker registry: `runtime.py:436 self.workers.register(...)`, `maestro/src/maestro/os/operating_system.py:39 self.runtime.register_worker(...)`.
- EXISTING work scheduler: `runtime.py:426 WorkItem(...)` and `runtime.py:432 self.scheduler.enqueue(...)`, plus existing fabric queue and OS async runner.
- IMPORTANT: `maestro/src/maestro/cognitive_fabric/fabric.py:30 self.executor.execute(...)` is a **different `CognitiveFabricExecutor`** from `autonomous.executor.CouncilExecutor` in the current published source. Do not merge these by name or claim that generic cognitive execution is proof of domain Council adapter execution.
- In the examined published reference source, `CouncilExecutor.register(adapter)` installs a Council-specific adapter and `execute(request)` rejects an unregistered Council. **This exact adapter-registration behavior and actual registrations must still be checked in the current Mac version.** Having an executor object and a worker queue does NOT establish any real specialist can execute.
- Remaining C01 proof: on-Mac production-only search for `CouncilExecutor.register` / `self.executor.register` / concrete adapter implementations and their runtime initialization, worker `allowed_councils`, generation of `DagNode` from `GovernedCouncilGraph`, and receipt-bound domain Council execution / independent checks. Compare against existing tests and governance contracts; if bindings are absent, prefer minimum safe wiring rather than parallel architecture.
- Guardian C01 status: **`UNVERIFIED`**, incomplete but narrowing. **C02 BLOCKED** pending adapter and graph evidence. No source writes, no new Council/Guardian/executor, no validated UDP runtime adoption. G1/G2/G3 release gates remain BLOCKED.

