# webiso

Extraction structurelle de pages HTML en 3 couches (**métadonnées** · **structure** ·
**contenu**) et comparaison d'un site **vrai** (référence) et d'un site **faux**
(candidat) — labels génériques, la comparaison reste symétrique entre deux URLs
quelconques — à **deux niveaux** avec [NetworkX](https://networkx.org/) :

- **Niveau 1 — structure complète** : **un seul graphe orienté, non segmenté,
  par site**, portant sur *tout l'arbre DOM* (chaque balise du document est un
  sommet, chaque arc une relation parent→enfant réelle — pas de filtrage par
  couche ni par liste de balises). Test d'isomorphisme VF2
  (`networkx.algorithms.isomorphism.DiGraphMatcher`).
- **Niveau 2 — contenu des balises Méta et Contenu** : un graphe de
  co-occurrence de mots non orienté par couche (sommets = mots, arcs =
  co-occurrence dans une même phrase du contenu porté par les balises de cette
  couche), pour les couches **Méta** et **Contenu** uniquement — la couche
  Structure (div, nav, header...) n'a pas de contenu textuel qui lui soit
  propre et en est exclue. Test d'isomorphisme VF2 sur graphe non orienté
  (`networkx.algorithms.isomorphism.GraphMatcher`). Le "contenu" de chaque
  couche réutilise les champs déjà extraits :
  - Méta → texte des balises (title, description, mots-clés...)
  - Contenu → texte visible (titres, paragraphes, liens, attributs alt...)

  Deux pages différentes ont presque toujours un vocabulaire de taille
  différente : un verdict « non isomorphe » au niveau 2 est donc attendu la
  plupart du temps — c'est un test d'identité stricte du contenu, pas une
  mesure de similarité approximative.

Les deux niveaux sont rapportés séparément (pas de verdict combiné automatique) :
« même structure ? » et « même contenu ? » sont deux questions distinctes.

Package issu du notebook `struct_complet.ipynb` : la logique d'extraction est
inchangée (toujours utilisée pour les tableaux d'affichage), le moteur SVG fait
main a été remplacé par des `networkx.DiGraph`/`networkx.Graph` + un layout
ressort (`networkx.spring_layout`, nœuds circulaires dont la taille suit le
degré), et l'algorithme VF2 codé à la main a été remplacé par
`networkx.algorithms.isomorphism`. Une interface web
[Streamlit](https://streamlit.io/) est fournie comme frontend.

## Installation

### macOS

```bash
cd webiso
pip install -e .
```

### Ubuntu / Debian

Python est déjà présent par défaut sur Ubuntu, mais `pip` et `venv` ne le sont pas
toujours. Dans un terminal :

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv
```

Puis, à l'intérieur du dossier `webiso` reçu :

```bash
cd webiso
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

L'environnement virtuel (`venv`) évite d'installer les dépendances au niveau
système. Il doit être réactivé (`source venv/bin/activate`) à chaque nouvelle
session de terminal avant de lancer `webiso-app` ou `webiso-compare`. Ce dossier
`venv/` ne doit jamais être commité dans git (il est exclu via `.gitignore`).

## Interface web (Streamlit)

```bash
webiso-app
```

Ouvre une page web (par défaut sur http://localhost:8501) avec un champ URL
« vrai » et un champ URL « faux », un bouton « Comparer », les tableaux
d'extraction, puis les deux niveaux de comparaison : Niveau 1 (1 graphe complet
par site + verdict VF2) et Niveau 2 (graphes de mots Méta + Contenu par site +
verdict VF2 par couche).

Équivalent sans passer par la commande installée :

```bash
streamlit run src/webiso/app_ui.py
```

**Sur un serveur Ubuntu sans interface graphique** (VM distante, WSL, etc.) :
Streamlit démarre quand même — c'est un serveur web, pas une fenêtre. Il faut
juste ouvrir l'URL affichée (`http://localhost:8501`) depuis un navigateur, sur
la même machine ou, si c'est une machine distante, en s'y connectant en SSH avec
redirection de port :

```bash
ssh -L 8501:localhost:8501 utilisateur@machine_distante
```

puis ouvrir `http://localhost:8501` dans le navigateur local.

## Déploiement sur Streamlit Cloud

1. Pousser **le contenu de ce dossier `webiso`** (pas le dossier parent) comme
   dépôt GitHub — `pyproject.toml` et `requirements.txt` doivent être à la racine
   du dépôt.
2. Sur [share.streamlit.io](https://share.streamlit.io), créer une nouvelle app en
   pointant sur ce dépôt, puis renseigner :
   - **Main file path** : `src/webiso/app_ui.py`
   - **Requirements file** : `requirements.txt` (détecté automatiquement — contient
     `-e .`, ce qui installe le package `webiso` et toutes ses dépendances déclarées
     dans `pyproject.toml`)

Si au lieu de ça c'est tout le dossier `Memoire Ruth Code` qui est poussé comme
dépôt (avec `webiso/` en sous-dossier), les chemins ci-dessus doivent être
préfixés par `webiso/` :
   - **Main file path** : `webiso/src/webiso/app_ui.py`
   - **Requirements file** : `webiso/requirements.txt`

   Dans ce cas, `requirements.txt` doit alors contenir `-e ./webiso` (chemin
   relatif à la racine du dépôt) plutôt que `-e .`.

### Version de Python

`scipy` (dépendance de `networkx.spring_layout`, utilisée pour dessiner les
graphes) ne dispose pas encore de wheels précompilées fiables pour les toutes
dernières versions de Python. Si Streamlit Cloud choisit par défaut une version
trop récente (ex. Python 3.14), l'installation de `scipy` peut échouer ou rester
incomplète, provoquant un `ModuleNotFoundError` au moment du rendu d'un graphe —
un échec qui peut ne pas apparaître sur un petit site (peu de sommets) mais se
déclencher sur un site plus volumineux empruntant le même chemin de code.

Deux garde-fous sont en place pour éviter ça :
- `pyproject.toml` déclare `requires-python = ">=3.9,<3.13"`, qui exclut les
  versions non testées ;
- `runtime.txt` (à la racine du dépôt) fixe explicitement `python-3.12`, la
  version utilisée pour tous les tests locaux de ce projet.

Si Streamlit Cloud ignore malgré tout ces fichiers, la version de Python peut
aussi se choisir manuellement dans les paramètres de l'application (**Manage
app → Settings → General → Python version**) : sélectionner **3.12**, puis
relancer un déploiement complet (**Reboot app**, ou supprimer puis recréer
l'app si le problème persiste).

## Utilisation en ligne de commande

```bash
webiso-compare https://exemple1.com https://exemple2.com
```

```bash
webiso-compare https://site-reference.com https://site-candidat.com
```

Génère les tableaux d'extraction, le graphe formel complet (console), 6 images
PNG (niveau 1 : 1 graphe complet × 2 sites, niveau 2 : 2 couches de mots ×
2 sites) et les deux rapports d'isomorphisme (structure, puis contenu).

## Utilisation programmatique

```python
from webiso import (
    analyser_site, dessiner_graphe, dessiner_graphe_mots, sauver_graphe, PALETTE_COMPLETE,
    test_isomorphisme_structure, test_isomorphisme_contenu,
)

vrai = analyser_site("https://site-reference.com")
faux = analyser_site("https://site-candidat.com")

# Niveau 1 — structure complète (un seul graphe non segmenté)
fig = dessiner_graphe(vrai["G_complet"], PALETTE_COMPLETE, "Structure — vrai")
sauver_graphe(fig, "structure_vrai.png")
iso_structure, mapping, rapport = test_isomorphisme_structure(vrai, faux)

# Niveau 2 — contenu des balises Méta et Contenu (graphes de mots)
iso_contenu, resultats_contenu = test_isomorphisme_contenu(vrai, faux)
```

Voir [`examples/comparer_deux_sites.py`](examples/comparer_deux_sites.py) pour un
exemple complet.

## Structure du package

| Module | Rôle |
|---|---|
| `webiso.fetch` | Validation d'URL et chargement HTTP |
| `webiso.extraction` | Extraction des 3 couches (méta / structure / contenu), pour les tableaux d'affichage |
| `webiso.graphs` | Niveau 1 : graphe complet et non segmenté de tout l'arbre DOM (`networkx.DiGraph`) |
| `webiso.textgraph` | Niveau 2 : graphe de co-occurrence de mots (`networkx.Graph`) pour les couches Méta et Contenu |
| `webiso.viz` | Dessin des graphes (NetworkX + Matplotlib), niveau 1 et niveau 2 |
| `webiso.isomorphism` | Tests d'isomorphisme VF2 — orienté (niveau 1) et non orienté (niveau 2) |
| `webiso.pipeline` | Orchestration : URL → HTML → graphes niveau 1 + niveau 2 |
| `webiso.cli` | Point d'entrée `webiso-compare` |
| `webiso.app_ui` | Page Streamlit (frontend), niveau 1 et niveau 2 |
| `webiso.webapp` | Point d'entrée `webiso-app` (lance `streamlit run` sur `app_ui.py`) |
