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

```bash
cd webiso
pip install -e .
```

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
