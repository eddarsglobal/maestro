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

---

<!-- MAESTRO_LIVE_WORK_ROADMAP_20261101_START -->
## 2026-11-01 — PRIORITÉ ABSOLUE : MAESTRO DOIT ACCOMPLIR DU TRAVAIL RÉEL

**Décision de l'audit Core + Gateway (01/11/2026).** Ne pas recommencer de zéro ; vérifier l'existant. Le Core a exécuté **1 435 tests Python réussis sur Mac** (journal utilisateur, 6,775 s, OK), mais **ce n'est pas une certification du travail accompli**. Le Gateway a fonctionné en conversation réelle, mais ni la fiabilité des missions complexes, ni la confidentialité complète des API, ni les effets vérifiables sur fichiers ne sont encore certifiés.

**Statut : `RELEASE=BLOCKED` ; `M0=OPEN/BLOCKED` ; `M1..M7=NOT_CERTIFIED`. Prochain travail autorisé : M0 uniquement.**

### Règles constitutionnelles

1. **Examiner avant de créer.** Réutiliser Core, Gateway, UI, système de missions, tests, journaux, permissions et Guardian existants ; ne pas dupliquer.
2. **Une identité publique MAESTRO, un seul moteur primaire local actif**, aucun cloud implicite ; les 18 Councils ne sont pas 18 IA autonomes. Le modèle technique déployé par l'équipe demeure privé dans le dialogue, l'UI, les endpoints destinés aux utilisateurs et les journaux publiés.
3. `CODE_PRESENT` ≠ `TESTS_PASS` ≠ `LIVE_EFFECT_VERIFIED` ≠ `CERTIFIED` ≠ `PRODUCTION`. HTTP 200, `/health`, tests simulés, build et 1 435 tests verts sont des éléments de preuve **partiels**.
4. Toute validation de fonctionnalité exige **une vraie exécution macOS**, un outil ou processus réel, une mesure avant/après indépendante, des résultats positifs **et négatifs**, la provenance exacte des trois commits et des logs minimisés. Mocks/fixtures : utiles en régression, **jamais suffisants comme preuve LIVE**.
5. Aucun outil, écriture, exécution, permission, suppression ou publication sans autorisation humaine quand requise ; environnement laboratoire isolé ; sauvegarde avant modification.
6. Le Guardian refuse les rapports déclaratifs `PASS`, les effets non observés, les fixtures présentées comme LIVE, les journaux tronqués et les preuves liées à un ancien commit. **Pas de certification par simple auto-déclaration.**
7. Progression stricte **M0 → M1 → M2 → M3 → M4 → M5 → M6 → M7**. Aucun passage à M(n+1) sans `M(n)=CERTIFIED` par contrôles indépendants et acceptation humaine, suivi de traçabilité Git local/Web. Pas de push automatique ni de force-push.
8. Toute modification après certification invalide l'attestation concernée jusqu'à requalification. Guardian rend `BLOCK` ou `REMEDIATE` avec cause et instructions de reprise, jamais de faux PASS.

### M0 — Provenance réelle et Guardian exécutable (P0) — OPEN/BLOCKED

- [ ] Vérifier sur Mac les trois dépôts officiels, branches, HEAD, fichiers suivis et non suivis, écarts GitHub, sauvegardes SHA-256, processus réellement actifs et sources effectivement exécutées. Préserver les modifications locales.
- [ ] Examiner le **Guardian existant** : `agents/Roadmap_guardian.py` est un adaptateur Git, pas un certificateur. Établir collecte de preuves LIVE et refuser les reçus fabriqués, logs simulés, commits périmés, preuves sans effets.
- [ ] Faire revoir l'inventaire et le protocole par le propriétaire avant de synchroniser des changements publics.
- **Preuve attendue :** rapports horodatés, hachages et commits complets, journal du contrôle réel et tests négatifs Guardian. **M0 non certifié.**

### M1 — Tracer une mission réelle de bout en bout (P0) — OPEN/BLOCKED

- [ ] Sur Mac, de l'UI à `POST /mission`, suivre un même `request_id` à travers session, permissions, Core, inférence locale réelle, contrôle AY, événement TX et réponse livrée.
- [ ] Vérifier indépendamment réponse pertinente, statut de fin, temps réel et persistance après redémarrage. Sans modèle, session ou autorisation : refus correct ; `health=READY` ne suffit pas.
- **Preuve :** traces cohérentes avec artefacts réels et tests négatifs. **M1 non certifié.**

### M2 — Annulation, concurrence, persistance et crash réels (P0) — OPEN/BLOCKED

- [ ] Vraies missions simultanées : 2 conversations, 2 requêtes de la même conversation, stop pendant attente, inférence, recherche, outil et processus.
- [ ] Interrompre/reprendre Gateway dans un laboratoire : aucun double-effet, replay incertain bloqué, journal durable cohérent, états DAG, receipts et permission vérifiés.
- **Preuve :** captures avant/après et journal d'effets réels ; cas non testés restent BLOCK. **M2 non certifié.**

### M3 — Travail utile sur un projet isolé (P0) — OPEN/BLOCKED

- [ ] Projet logiciel de test avec défaut réel et tests rouges initialement.
- [ ] MAESTRO inspecte uniquement un workspace autorisé ; propose une correction avec diff précis sans écrire ; après approbation humaine explicite, applique le changement et lance les **vrais** tests/build.
- [ ] Vérifier les hachages et résultats avant/après, refuser accès hors scope et gérer échec/rollback ; aucune réussite prétendue sans fichier réellement modifié.
- **Preuve :** mission, autorisation, diff, fichier modifié, tests verts indépendants, reçu durable. **M3 non certifié.**

### M4 — Sécurité, confidentialité et vérité des API (P0) — OPEN/BLOCKED

- [ ] Auditer en réel `/models`, `/providers`, `/session`, `/health`, UI et logs : pas de fuite de l'identifiant interne du modèle vers un utilisateur non autorisé. Préserver diagnostic technique strictement réservé à l'équipe.
- [ ] Tester sur sockets localhost Host/Origin/session, accès Workspace, traversée de chemins, liens symboliques, refus de cloud et permissions.
- **Preuve :** essais positifs/négatifs, validation sécurité indépendante, pas de secret dans Git public. **M4 non certifié.**

### M5 — Qualité sémantique, contexte et huit langues (P0) — OPEN/BLOCKED

- [ ] Inférence réellement exécutée en EN (défaut), FR, DE, AR, PT, ES, HR, IT ; identité MAESTRO, confidentialité du modèle, capacité réelle sans hallucination.
- [ ] Conversation de 20 tours : mémoire du contexte, « votre projet » vs « mon projet », bascule de langue, format Markdown, refus de fausses capacités et reprise.
- [ ] Mesurer latences froid/chaud, P95, types d'échec ; évaluer réponses utiles avec relecteurs humains compétents dans les langues ; signaler les langues non qualifiées.
- **Preuve :** réponses réelles évaluées sans prompts privés publiés. **M5 non certifié.**

### M6 — Application installée sur Mac et régressions (P0) — OPEN/BLOCKED

- [ ] Sur application **installée**, vérifier accueil, paramètres/enregistrement, thèmes, huit langues, historique, stop, restauration ; ne pas assimiler build Vite ou localhost à installation.
- [ ] Rejouer M1–M5 sur le binaire exact ; démontrer intégrité de l'installation, absence de perte utilisateur, signature/notarisation si distribution externe.
- **Preuve :** binaire versionné, résultats LIVE, CI et revue indépendantes. **M6 non certifié.**

### M7 — Revue tri-repo, publication et décision de release (P0) — OPEN/BLOCKED

- [ ] Réconcilier Core/Gateway/UI sans écraser les changements locaux ; isoler identifiants privés et secrets ; réexaminer licences, CI et provenance.
- [ ] Publier par branches existantes et PRs revues, sans push automatique. Vérifier que tous les certificats M0–M6 portent sur les sources publiées exactes.
- [ ] Approbation propriétaire puis décision release distincte ; si P0, CI, macOS installé ou signature manquent : `NOT_PRODUCTION_READY`.
- **Preuve :** chaîne de certification complète, revue indépendante, validation propriétaire. **M7 non certifié.**

### Mission du RoadMapGuardian

Lire `RoadMapGuardian.md` et utiliser le programme existant `agents/Roadmap_guardian.py` comme **adaptateur de vérification**, non comme preuve d'autonomie. Son évolution doit ajouter vérification des effets LIVE, collecte des reçus et décisions `PASS_TESTS / LIVE_VERIFIED / CERTIFIED / REMEDIATE / BLOCK`, avec provenance exacte et contrôle humain. **L'ajout de ce texte ne lui confère pas encore ces capacités**.

**Verdict présent : `NEXT_WORK=M0` ; `NEXT_STAGE_AUTHORIZED=NO` ; `PRODUCTION=BLOCKED`.**
<!-- MAESTRO_LIVE_WORK_ROADMAP_20261101_END -->
