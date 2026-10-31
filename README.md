# MAESTRO — Votre assistant IA local / Your local AI assistant

**MAESTRO est un assistant d'intelligence artificielle local conçu par EddarsGlobal.** Il réunit une interface de conversation, un Gateway local et un moteur de gouvernance appelé MAESTRO Core.

> **MAESTRO COMMANDS MODELS. MODELS DO NOT COMMAND MAESTRO.**

**Langues de ce guide :** français (détaillé) · [English quick overview](#english-quick-overview).

> **Statut : projet en développement actif.** Le code public et les versions de laboratoire utilisées par l'équipe peuvent être différents. La réussite d'une installation ou des tests ne constitue pas une certification de production. Il n'existe pas encore d'installateur universel de bureau validé sur tous les systèmes.

## Sommaire

1. [Comprendre MAESTRO en une minute](#comprendre-maestro-en-une-minute)
2. [Ce qu'il permet de faire](#ce-quil-permet-de-faire)
3. [Les trois composants](#les-trois-composants)
4. [Avant l'installation](#avant-linstallation)
5. [Installer sur macOS — pas à pas](#installer-sur-macos--pas-à-pas)
6. [Premier démarrage](#premier-démarrage)
7. [Utiliser les conversations](#utiliser-les-conversations)
8. [Confidentialité et autorisations](#confidentialité-et-autorisations)
9. [Problèmes fréquents](#problèmes-fréquents)
10. [Tests et statut](#tests-et-statut)
11. [Pour les développeurs](#pour-les-développeurs)
12. [Aide, licence et contact](#aide-licence-et-contact)

## Comprendre MAESTRO en une minute

Imaginez un assistant auquel vous pouvez écrire : « Explique ce concept », « Aide-moi à rédiger un texte » ou « Analyse un projet ». MAESTRO présente la conversation et fait appel aux composants locaux autorisés pour produire une réponse.

**Local** signifie que le Gateway, les données de conversation et le moteur d'inférence peuvent fonctionner sur votre propre machine. Cela ne veut **pas** dire que chaque fonctionnalité est disponible sans configuration, ni que toute action externe est automatiquement autorisée.

**MAESTRO n'est pas le nom de son modèle de langage.** L'assistant possède une identité de produit distincte de son moteur technique. Les configurations précises du moteur déployé ne sont pas publiées dans ce guide.

## Ce qu'il permet de faire

Selon la version, les composants installés et les autorisations :
- discuter, expliquer des notions, rédiger, reformuler et aider à réfléchir ;
- conserver des conversations locales, les retrouver, les renommer et les gérer ;
- proposer une aide au développement logiciel ;
- analyser des fichiers dans un espace de travail **explicitement autorisé**, lorsque cette capacité est disponible ;
- enregistrer des traces et des vérifications internes pour diagnostiquer une mission ;
- appliquer des limites d'exécution et demander l'autorisation humaine lorsque nécessaire.

**Ce qu'il ne faut pas supposer :** accès à tous les fichiers du Mac, navigation Web automatique, capacité juridique certifiée, autonomie sans limites, absence totale d'erreurs ou disponibilité universelle sur Windows/Linux. La qualité d'une réponse doit toujours être évaluée séparément du succès technique d'une mission.

## Les trois composants

| Composant | Rôle | Dépôt |
| --- | --- | --- |
| **MAESTRO Core** | Contrôle des missions, gouvernance, permissions, preuves et états | [maestro](https://github.com/eddarsglobal/maestro) |
| **Local Gateway** | Serveur local reliant les fonctions du Core et l'interface | [maestro-gateway](https://github.com/eddarsglobal/maestro-gateway) |
| **Interface UI** | Pages, conversations et paramètres visibles | [maestro-ui](https://github.com/eddarsglobal/maestro-ui) |

```text
Vous écrivez dans MAESTRO UI
            |
            v
    Local Gateway
            |
            v
      MAESTRO Core
            |
            v
    Ressources autorisées
```

Les responsabilités spécialisées (appelées « Councils » dans l'architecture) sont internes : l'utilisateur doit recevoir une réponse normale de MAESTRO, pas une liste de Councils ou de transactions techniques.

## Avant l'installation

Ce guide décrit **une installation depuis les sources pour l'essai local**, et non un produit certifié prêt à distribuer.

**À prévoir sur macOS :**
- un Mac avec connexion Internet pour télécharger le code et les dépendances ;
- **Git** : `git --version` ;
- **Python 3.11 ou plus récent** (Python 3.12 conseillé) : `python3 --version` ;
- **Node.js et npm** compatibles avec le projet Vite : `node --version` et `npm --version` ;
- un runtime d'IA locale compatible, installé et configuré séparément selon les instructions de votre environnement ;
- de l'espace disque et de la mémoire adaptés au moteur local retenu.

Si une commande est « not found », installez cet outil depuis son fournisseur officiel avant de poursuivre. Ne copiez pas aveuglément des commandes exigeant des droits administrateur.

**Windows et Linux :** le code vise la portabilité, mais le parcours complet ci-dessous est documenté pour macOS ; il ne constitue pas une validation de bout en bout de ces plateformes.

## Installer sur macOS — pas à pas

Ouvrez **Terminal** (Applications → Utilitaires → Terminal). Copiez chaque bloc séparément. Les commandes ci-dessous ne suppriment ni fichiers ni conversations.

### Étape 1 — Télécharger les trois dépôts

```bash
mkdir -p "$HOME/MAESTRO"
cd "$HOME/MAESTRO"
git clone https://github.com/eddarsglobal/maestro.git
git clone https://github.com/eddarsglobal/maestro-gateway.git
git clone https://github.com/eddarsglobal/maestro-ui.git
```

Vous devez obtenir trois dossiers **frères** : `maestro/`, `maestro-gateway/` et `maestro-ui/`. Si vous possédez déjà ces dossiers avec des modifications personnelles, **ne relancez pas ces clones et ne les remplacez pas**.

### Étape 2 — Vérifier Python

```bash
python3 --version
node --version
npm --version
```

Si votre commande Python est ancienne, utilisez explicitement le Python 3.12 installé sur le Mac (par exemple `python3.12`) dans l'étape suivante.

### Étape 3 — Préparer l'environnement Python isolé

```bash
cd "$HOME/MAESTRO"
python3 -m venv maestro-gateway/.venv
./maestro-gateway/.venv/bin/python -m pip install --upgrade pip setuptools wheel
./maestro-gateway/.venv/bin/python -m pip install -e ./maestro -e ./maestro-gateway
```

Un **environnement virtuel** empêche de mélanger les dépendances de MAESTRO avec celles d'autres logiciels du Mac. Cette étape ne démarre pas l'assistant.

### Étape 4 — Construire l'interface

```bash
cd "$HOME/MAESTRO/maestro-ui"
npm ci
npm run build
```

Le résultat attendu est un dossier `maestro-ui/dist`. Si la compilation échoue, consultez le texte de l'erreur avant de tenter une autre installation.

### Étape 5 — Vérifier le moteur local

Le moteur de langage est géré séparément de l'interface. **Son installation et sa sélection précises dépendent de la configuration autorisée.** Ne supposez pas qu'un modèle quelconque téléchargé sur Internet sera fonctionnel dans MAESTRO.

Pour un runtime local compatible disposant d'une API de contrôle, vérifiez d'abord qu'il est réellement démarré et qu'un modèle autorisé est disponible. Le Gateway peut fonctionner sans mission d'inférence réussie ; un état HTTP sain ne prouve pas qu'une conversation fonctionnera.

## Premier démarrage

Depuis un nouveau Terminal :

```bash
cd "$HOME/MAESTRO"
MAESTRO_UI_DIST_DIR="$HOME/MAESTRO/maestro-ui/dist" \
  ./maestro-gateway/.venv/bin/python -m maestro_gateway
```

Laissez le Terminal ouvert. Dans le navigateur du **même Mac**, ouvrez :

**http://127.0.0.1:8787/app/**

Vous pouvez vérifier le serveur avec une deuxième fenêtre Terminal :

```bash
curl -fsS http://127.0.0.1:8787/health
```

**Important :** `/health` vérifie le Gateway, pas la bonne configuration de l'IA. Faites ensuite un essai dans l'interface. Pour arrêter ce serveur lancé manuellement, revenez au Terminal concerné et utilisez **Ctrl+C**.

Dans certaines versions de développement, des réglages supplémentaires sont requis pour le moteur IA et les outils. N'exposez pas le port local à Internet et n'activez pas des permissions que vous ne comprenez pas.

## Utiliser les conversations

Pour débuter, essayez des messages simples :
- « Explique-moi la différence entre un fichier et un dossier. »
- « Aide-moi à rédiger un courrier professionnel. »
- « Résume ces idées en cinq lignes. »

Vous pouvez ensuite poursuivre la conversation. Les fonctionnalités de recherche, archivage, copie et suppression varient selon la version réellement installée.

**Attention à la suppression :** supprimer les conversations n'est pas la même chose que vider les journaux, les preuves, l'historique des missions ou la configuration. Sauvegardez les conversations importantes avant toute action irréversible. Ne supprimez jamais le dossier `~/.maestro` pour « nettoyer » sans un inventaire préalable.

## Confidentialité et autorisations

- Le Gateway est conçu pour écouter **en boucle locale** (par défaut `127.0.0.1:8787`).
- Un navigateur ouvert sur une autre machine n'accède pas automatiquement à ce serveur.
- Les conversations et les informations de diagnostic peuvent contenir des données personnelles : ne publiez jamais vos journaux bruts.
- L'accès à un dossier, l'exécution d'une commande ou une opération externe doivent respecter les permissions effectives.
- Le nom du moteur IA choisi par l'équipe est un détail d'implémentation interne et ne fait pas partie de la présentation publique de MAESTRO.
- Le code ouvert et les documents ne doivent contenir aucun mot de passe, jeton API ni secret de production.

## Problèmes fréquents

| Symptôme | Vérification de débutant |
| --- | --- |
| `git: command not found` | Installer les outils de développement Git compatibles avec macOS |
| Python trop ancien | Utiliser Python 3.11+ ; vérifier le Python utilisé par `.venv` |
| `npm: command not found` | Installer Node.js/npm, puis rouvrir Terminal |
| `npm ci` échoue | Vérifier la version de Node, l'accès réseau et conserver le message d'erreur |
| La page ne s'ouvre pas | Vérifier que le Gateway est toujours lancé et que le port 8787 écoute |
| Ancien design affiché | Relancer `npm run build`, vérifier `MAESTRO_UI_DIST_DIR` puis recharger sans cache |
| Gateway sain mais aucune réponse | Vérifier le moteur local, sa configuration et les journaux d'erreur ; ne pas confondre santé et inférence |
| Un fichier est inaccessible | Vérifier que l'espace de travail et les permissions ont été accordés |
| Une réponse paraît fausse | Vérifier les faits auprès de sources fiables ; signaler le problème avec données privées masquées |

En cas de blocage, collectez : version de macOS, versions Python/Node, commande exécutée, erreur exacte et commit Git (`git rev-parse --short HEAD`). **Ne publiez pas vos conversations privées ni vos fichiers de configuration contenant des secrets.**

## Tests et statut

Pour tester les composants **sans confondre tests et production** :

```bash
cd "$HOME/MAESTRO/maestro"
../maestro-gateway/.venv/bin/python -m unittest discover -s tests -q
```

La baseline historique Core v1.1.0 R1 annonçait **283 tests**, mais le nombre réel dépend du commit. Le test d'intégration réel, les permissions, l'interface et l'exécution d'une requête sont des contrôles distincts.

Le projet évolue : n'interprétez pas la présence d'un écran ou d'une API comme la preuve qu'une fonctionnalité est certifiée.

## Pour les développeurs

Commencez par [docs/INSTALLATION.md](docs/INSTALLATION.md), [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md), [SECURITY.md](SECURITY.md) et les tests. Les descriptions avancées des responsabilités internes sont dans [docs/COUNCILS.md](docs/COUNCILS.md) et [blueprints/](blueprints/).

**Important pour la synchronisation Git :** avant un `pull`, `checkout`, `reset` ou `push`, vérifier la branche, les modifications locales et les fichiers non suivis. Ne pas synchroniser des paramètres de modèles internes, données utilisateur ou secrets dans un dépôt public.

## Aide, licence et contact

- [GitHub officiel](https://github.com/eddarsglobal/maestro)
- [Problèmes et demandes](https://github.com/eddarsglobal/maestro/issues)
- Sécurité : [SECURITY.md](SECURITY.md) — signalement privé : **maestro.men@gmail.com**
- Licence communautaire du Core : [AGPL-3.0-or-later](LICENSE) ; [conditions commerciales](COMMERCIAL_LICENSE.md)
- Création et stewardship : **EddarsGlobal**
- Site du projet : **https://maestro.men** (la disponibilité du site ne garantit pas celle d'un service hébergé)

## English quick overview

MAESTRO is a **local-first AI assistant project** by EddarsGlobal. It consists of a Python Core, a local Python Gateway and a React/Vite user interface. The repositories are open for development and evaluation; the current public source tree is not a certified, one-click consumer release.

To try it on macOS: install Git, Python 3.11+ and compatible Node.js/npm; clone the three sibling repositories above; create a Python virtual environment and install Core + Gateway; run `npm ci` and `npm run build` inside `maestro-ui`; then start the Gateway with `MAESTRO_UI_DIST_DIR` pointing to `maestro-ui/dist`. Open `http://127.0.0.1:8787/app/`. Inference requires a separately configured authorized local engine. Never publish secrets, user conversations or internal model configuration. See the French step-by-step instructions and component READMEs for details.

---

**MAESTRO COMMANDS MODELS. MODELS DO NOT COMMAND MAESTRO.**
