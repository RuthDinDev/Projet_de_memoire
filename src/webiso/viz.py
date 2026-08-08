"""Visualisation des graphes formels avec NetworkX + Matplotlib.

Remplace l'ancien moteur SVG fait main : les nœuds sont disposés par un layout de
type ressort (``networkx.spring_layout``) — organisation libre selon les
connexions, pas par couche/profondeur —, dessinés en cercles dont la taille suit le
degré (les nœuds les plus connectés apparaissent plus gros), colorés selon la
palette de la couche sémantique (méta / structure / contenu), et reliés par des
arcs dessinés avec ``networkx.draw_networkx_edges``.
"""

import matplotlib
matplotlib.use("Agg")  # backend non interactif : évite les crashs GUI hors thread principal (Streamlit)

import networkx as nx
import matplotlib.pyplot as plt

FOND = "#f8f7f4"
COULEUR_ARC = "#c8c6be"
COULEUR_DEFAUT = "#888780"

TAILLE_BASE = 300
TAILLE_PAR_DEGRE = 350


def dessiner_graphe(G, palette, titre="Graphe", ax=None, figsize=(11, 7), seed=42):
    """Dessine ``G`` (un ``networkx.DiGraph`` avec attributs ``tag``/``depth``) et
    retourne la ``Figure`` matplotlib correspondante."""
    if G.number_of_nodes() == 0:
        raise ValueError("Graphe vide : aucun nœud à dessiner.")

    pos = nx.spring_layout(G, seed=seed)

    couleurs = [palette.get(data["tag"], COULEUR_DEFAUT) for _, data in G.nodes(data=True)]
    labels = {n: f"<{data['tag']}>" for n, data in G.nodes(data=True)}
    degres = dict(G.degree())
    tailles = [TAILLE_BASE + TAILLE_PAR_DEGRE * degres[n] for n in G.nodes()]

    fig = None
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    fig.patch.set_facecolor(FOND)
    ax.set_facecolor(FOND)
    ax.set_title(titre, fontsize=12, fontfamily="sans-serif", color="#1a1917")

    nx.draw_networkx_nodes(G, pos, node_color=couleurs, node_shape="o",
                            node_size=tailles, edgecolors="white", linewidths=1.2, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color=COULEUR_ARC, arrows=True,
                            arrowstyle="-|>", arrowsize=10,
                            connectionstyle="arc3,rad=0.08", ax=ax)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7,
                             font_family="monospace", ax=ax)

    ax.axis("off")
    fig.tight_layout()
    return fig


def sauver_graphe(fig, chemin, dpi=150):
    fig.savefig(chemin, dpi=dpi, bbox_inches="tight", facecolor=FOND)
    print(f"  ✓  Sauvegardé : {chemin}")


def afficher_graphe(fig):
    """Affiche la figure (notebook : rendu inline : script : fenêtre matplotlib)."""
    try:
        from IPython.display import display
        display(fig)
    except ImportError:
        plt.show()
