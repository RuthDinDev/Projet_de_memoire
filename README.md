# webiso

Extraction structurelle de pages HTML en 3 couches (**métadonnées** · **structure** ·
**contenu**), construction d'un graphe formel `G=(S,A)` par couche avec
[NetworkX](https://networkx.org/), visualisation via NetworkX/Matplotlib, et test
d'isomorphisme structurel (VF2) entre deux sites.

Package issu du notebook `struct_complet.ipynb` : la logique d'extraction est
inchangée, le moteur SVG fait main a été remplacé par des `networkx.DiGraph` +
un layout ressort (`networkx.spring_layout`, nœuds circulaires dont la taille suit
le degré), et l'algorithme VF2 codé à la main a été remplacé par
`networkx.algorithms.isomorphism.DiGraphMatcher`. Une interface web
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

Ouvre une page web (par défaut sur http://localhost:8501) avec deux champs d'URL,
un bouton « Comparer », les tableaux d'extraction, les 6 graphes NetworkX (méta /
structure / contenu × 2 sites) et le rapport d'isomorphisme VF2, couche par couche.

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

## Utilisation en ligne de commande

```bash
webiso-compare https://exemple1.com https://exemple2.com
```

Génère les tableaux d'extraction, les graphes formels (console), 6 images PNG
(3 couches × 2 sites) et le rapport d'isomorphisme final.

## Utilisation programmatique

```python
from webiso import analyser_site, dessiner_graphe, sauver_graphe, PALETTES, test_isomorphisme_complet

site1 = analyser_site("https://exemple1.com")
site2 = analyser_site("https://exemple2.com")

fig = dessiner_graphe(site1["G_struct"], PALETTES["struct"], "Structure — site1")
sauver_graphe(fig, "structure_site1.png")

iso_global, resultats = test_isomorphisme_complet(site1, site2)
```

Voir [`examples/comparer_deux_sites.py`](examples/comparer_deux_sites.py) pour un
exemple complet.

## Structure du package

| Module | Rôle |
|---|---|
| `webiso.fetch` | Validation d'URL et chargement HTTP |
| `webiso.extraction` | Extraction des 3 couches (méta / structure / contenu) |
| `webiso.graphs` | Construction du graphe formel `G=(S,A)` en `networkx.DiGraph` |
| `webiso.viz` | Dessin des graphes (NetworkX + Matplotlib) |
| `webiso.isomorphism` | Test d'isomorphisme VF2 via `networkx.algorithms.isomorphism` |
| `webiso.pipeline` | Orchestration : URL → HTML → 3 graphes |
| `webiso.cli` | Point d'entrée `webiso-compare` |
| `webiso.app_ui` | Page Streamlit (frontend) |
| `webiso.webapp` | Point d'entrée `webiso-app` (lance `streamlit run` sur `app_ui.py`) |
