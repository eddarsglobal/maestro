# Installer MAESTRO depuis les sources — guide pas à pas

**Public concerné :** personnes débutantes sur macOS, développeurs qui veulent reproduire un environnement local. Il ne s'agit pas d'un installateur de produit fini.

**Liens :** [README principal](../README.md) · [Gateway](https://github.com/eddarsglobal/maestro-gateway) · [UI](https://github.com/eddarsglobal/maestro-ui).

## 0. Comprendre ce que vous installez

Vous installez trois dépôts : le **Core** (règles et missions), le **Gateway** (serveur localhost) et la **UI** (application dans le navigateur). Un modèle IA local autorisé doit être disponible pour obtenir une réponse en conversation ; les détails du modèle déployé sont internes à l'équipe.

La version GitHub publique et les versions expérimentales sur le Mac d'un développeur peuvent ne pas être identiques. **N'utilisez pas ce guide pour écraser une installation existante avec des correctifs locaux non publiés.**

## 1. Vérifier les outils sur le Mac

Ouvrir Terminal, puis exécuter :

```bash
git --version
python3 --version
node --version
npm --version
```

Requis : Git, Python 3.11+ (3.12 recommandé), Node/npm compatibles avec Vite. Si une commande est introuvable, installer l'outil officiel correspondant et rouvrir Terminal.

## 2. Cloner les trois dépôts

```bash
mkdir -p "$HOME/MAESTRO"
cd "$HOME/MAESTRO"
git clone https://github.com/eddarsglobal/maestro.git
git clone https://github.com/eddarsglobal/maestro-gateway.git
git clone https://github.com/eddarsglobal/maestro-ui.git
```

Les trois dossiers doivent être situés côte à côte. Ne relancez pas `git clone` sur des répertoires déjà présents.

## 3. Installer Python dans un environnement isolé

```bash
cd "$HOME/MAESTRO"
python3 -m venv maestro-gateway/.venv
./maestro-gateway/.venv/bin/python -m pip install --upgrade pip setuptools wheel
./maestro-gateway/.venv/bin/python -m pip install -e ./maestro -e ./maestro-gateway
```

**Pourquoi ?** Un environnement virtuel préserve les autres programmes Python du Mac. Si vous disposez de Python 3.12 sous le nom `python3.12`, utilisez-le pour créer l'environnement.

## 4. Construire l'interface

```bash
cd "$HOME/MAESTRO/maestro-ui"
npm ci
npm run build
```

Vérifiez la création du dossier `dist`. La compilation de la UI ne démarre pas l'assistant.

## 5. Démarrer le Gateway

```bash
cd "$HOME/MAESTRO"
MAESTRO_UI_DIST_DIR="$HOME/MAESTRO/maestro-ui/dist" \
  ./maestro-gateway/.venv/bin/python -m maestro_gateway
```

**Gardez la fenêtre ouverte.** Dans un navigateur sur ce même ordinateur, ouvrez `http://127.0.0.1:8787/app/`.

Autre Terminal, diagnostic :

```bash
curl -fsS http://127.0.0.1:8787/health
```

Une réponse de santé confirme seulement que le Gateway répond. Pour discuter avec MAESTRO, la configuration du moteur local est nécessaire ; elle n'est pas automatiquement fournie par ce clonage.

## 6. Premier essai utilisateur

Essayez « Bonjour, présente-toi brièvement. » Si aucune réponse n'arrive, séparez le diagnostic :
1. la page se charge-t-elle ?
2. le Gateway répond-il à `/health` ?
3. le moteur autorisé est-il disponible ?
4. la mission renvoie-t-elle une erreur ou une demande d'autorisation ?

Si MAESTRO invente une capacité ou produit une réponse incorrecte, il s'agit d'un défaut fonctionnel, même si les tests techniques passent.

## 7. Sauvegarde et mises à jour

Avant de synchroniser un dépôt existant :

```bash
cd "$HOME/MAESTRO/maestro"
git status --short
git branch --show-current
git log -1 --oneline
```

Ne pas utiliser `git reset --hard`, `git clean` ni `git checkout` aveuglément sur un dossier contenant des modifications locales. Ne pas publier secrets, réglages internes, conversations, ou fichiers runtime.

La présence de nouveaux commits sur GitHub n'autorise pas à écraser des correctifs locaux non synchronisés.

## 8. Dépannage rapide

| Erreur ou symptôme | Vérification |
| --- | --- |
| Python incompatible | Vérifier le Python ayant créé `.venv` |
| Installation pip échoue | Copier l'erreur exacte ; vérifier réseau et venv |
| `npm ci` échoue | Vérifier Node/npm compatibles et `package-lock.json` |
| Port 8787 occupé | `lsof -nP -iTCP:8787 -sTCP:LISTEN` ; identifier avant tout arrêt |
| Interface ancienne | Reconstruire `dist`, vérifier `MAESTRO_UI_DIST_DIR`, recharger sans cache |
| Erreur d'autorisation | Vérifier la permission, ne pas désactiver les contrôles |
| Pas de modèle | Configuration du runtime local à examiner ; aucune sélection secrète publiée ici |

## 9. Pour tester le Core

```bash
cd "$HOME/MAESTRO/maestro"
../maestro-gateway/.venv/bin/python -m unittest discover -s tests -q
```

Les tests peuvent varier selon la version. Un succès ici ne teste ni l'interface, ni les réponses du modèle, ni les opérations en conditions réelles.

## 10. Confidentialité, sécurité et limites

- Utiliser le Gateway localement, pas en exposition publique.
- Les journaux peuvent contenir des informations privées ; les masquer avant partage.
- Ne jamais effacer `~/.maestro` pour corriger un problème visuel.
- Aucune réponse juridique, financière ou médicale n'est automatiquement certifiée.
- macOS : procédure ci-dessus ; Windows/Linux : pas de validation équivalente déclarée par cette documentation.
- Pas de promesse de production : le projet est toujours en développement.

**Besoin d'aide ?** Ouvrir une [Issue](https://github.com/eddarsglobal/maestro/issues) sans secrets, ou consulter la [politique de sécurité](../SECURITY.md). Contact : maestro.men@gmail.com.
