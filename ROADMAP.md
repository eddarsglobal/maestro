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

<!-- MAESTRO-P043C0-URGENT-START -->
## P0 CRITICAL — Restaurer la chaîne conversationnelle réelle (URGENT, BLOCK)

**Tâche impérative, à appliquer avant toute nouvelle annonce de réussite conversationnelle :**
> C'est de corriger la chaîne réelle entrée utilisateur → détection linguistique → sélection du modèle → génération → contrôle qualité → affichage.

**Incident LIVE utilisateur — 24 octobre 2026** :
- `wer bist du?` (DE) a produit « Ich bin Qwen, der von Alibaba Cloud entwickelt wurde. » : **FAIL identité de l'assistant**. MAESTRO reste MAESTRO, le modèle et son fournisseur sont des attributs transparents vérifiés dans le runtime lorsqu'ils sont demandés.
- `sta mozes raditi` (HR sans diacritiques) a échoué sur « Response generation exhausted its configured token budget (192) » : **FAIL livraison/gestion du budget**. Aucune génération partielle ne doit être présentée comme un succès.
- `dobar dan` (HR) a produit « Hallo! Wie geht es Ihnen heute? » : **FAIL langue courante**. La langue du message courant prime sur la langue de l'UI et sur les tours précédents, sauf demande explicite contraire ou ambiguïté démontrée.

**Preuve quantitative existante** : `MAESTRO_SIQ_20261023_190709.json`, SHA-256 `d60f7d3df0e2b4635fbbf38d33349a7d30ed2d2cd7df4e8728396b17bde6c7c5` ; 226 exécutés, 88 PASS_OBJECTIVE, 116 FAIL, 22 OBSERVED_UNVERIFIED. Croate : 21 FAIL sur 26 ; arabe : 20 FAIL sur 26 ; verdict Guardian `BLOCK`, `language_fluency_certified=false`.

### Ordre d'exécution obligatoire
1. **Entrée** : tracer langue du message courant, langue explicite demandée, langue UI, contexte de conversation, identifiant de requête, sans exposer de données personnelles.
2. **Détection linguistique** : diagnostiquer et corriger les erreurs HR (y compris sans diacritiques), DE et changements de langue ; préserver EN/FR/DE/AR/PT/ES/HR/IT, sans priorité spéciale au français.
3. **Sélection du modèle** : enregistrer l'ID exact du modèle réellement choisi, sa version/digest et la raison de sélection ; ne jamais confondre fournisseur du modèle et identité MAESTRO ; zéro cloud, zéro téléchargement automatique.
4. **Génération** : examiner le raccourci `fast_intro` / budget 192, classifier les dépassements et gérer un éventuel nouvel essai borné seulement si les effets et le transport le permettent ; ne pas introduire de boucle infinie ni de concurrence avec le Primary.
5. **Contrôle qualité** : évaluer identité factuelle, langue réellement écrite, pertinence, complétude et budget. Les jugements doivent venir du texte réellement généré, avec raisons vérifiables ; aucun PASS déduit de HTTP 200 ni de réponses déterministes comme `433`.
6. **Affichage** : vérifier la réponse vue dans l'UI React ORIGINALE, avec origine du modèle et statut d'erreur sans masquage. **INTERDICTION de modifier, remplacer, reconstruire ou substituer l'UI originale** pour cette tâche.
7. **Validation Mac LIVE** : refaire les 3 prompts fautifs en interface, puis une matrice 8 langues, alternance DE→HR→DE, réponses longues, budgets bas, redémarrage et persistance ; preuves textuelles/trace par mission ; toute régression critique bloque la certification.
8. **Gouvernance** : régressions Core/Gateway sont nécessaires mais insuffisantes. `PASS_TECHNICAL` et `PASS_CONVERSATIONAL` sont deux verdicts distincts. Aucun checkpoint « stable » ni promotion automatique avant preuves LIVE et approbation Guardian.

**Invariants** : Primary local souverain unique, aucune inférence idle non certifiée, aucun téléchargement de modèles, Core zéro-modèle préservé, preuve d'arrêt fournisseur et coordination de tous les chemins restent BLOCK. Ne jamais masquer les FAIL historiques.

**Statut au 24 octobre 2026** : `P0_CRITICAL / REMEDIATE`, aucune correction de production installée par cette seule mise à jour RoadMap.
<!-- MAESTRO-P043C0-URGENT-END -->
