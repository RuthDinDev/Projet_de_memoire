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


def dessiner_graphe(G, palette, titre="Graphe", ax=None, figsize=(12, 8), seed=42, max_labels=80):
    """Dessine ``G`` (un ``networkx.DiGraph`` avec attributs ``tag``/``depth``) et
    retourne la ``Figure`` matplotlib correspondante.

    ``G`` est désormais typiquement le graphe complet d'une page entière (toutes
    les balises du DOM, voir ``webiso.graphs.construire_graphe_complet``) et peut
    donc compter plusieurs centaines de sommets : seuls les ``max_labels``
    sommets les plus connectés sont étiquetés, pour garder la figure lisible
    (tous les sommets restent dessinés)."""
    if G.number_of_nodes() == 0:
        raise ValueError("Graphe vide : aucun nœud à dessiner.")

    pos = nx.spring_layout(G, seed=seed)

    couleurs = [palette.get(data["tag"], COULEUR_DEFAUT) for _, data in G.nodes(data=True)]
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

    artiste_noeuds = nx.draw_networkx_nodes(G, pos, node_color=couleurs, node_shape="o",
                                             node_size=tailles, edgecolors="white",
                                             linewidths=1.2, ax=ax)
    artistes_arcs = nx.draw_networkx_edges(G, pos, edge_color=COULEUR_ARC, arrows=True,
                                            arrowstyle="-|>", arrowsize=10,
                                            connectionstyle="arc3,rad=0.08", ax=ax)
    # networkx place toujours les nœuds au-dessus des arcs (zorder fixe, quel que
    # soit l'ordre d'appel) : dans un graphe dense où les nœuds se chevauchent,
    # les arcs entre eux deviennent invisibles. On force l'ordre inverse.
    artiste_noeuds.set_zorder(1)
    for artiste in (artistes_arcs if isinstance(artistes_arcs, list) else [artistes_arcs]):
        artiste.set_zorder(2)

    top_noeuds = sorted(degres, key=degres.get, reverse=True)[:max_labels]
    tags = nx.get_node_attributes(G, "tag")
    labels = {n: f"<{tags[n]}>" for n in top_noeuds}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7,
                             font_family="monospace", ax=ax)

    ax.axis("off")
    fig.tight_layout()
    return fig


def dessiner_graphe_mots(G, couleur, titre="Graphe de mots", ax=None, figsize=(11, 7),
                          seed=42, max_labels=40):
    """Dessine un graphe de co-occurrence de mots (``networkx.Graph`` non orienté,
    voir :mod:`webiso.textgraph`) et retourne la ``Figure`` matplotlib.

    Contrairement à ``dessiner_graphe`` (niveau 1) : pas de flèches (relation
    symétrique), étiquette = le mot lui-même, épaisseur d'arc proportionnelle au
    nombre de co-occurrences. Une page peut contenir des centaines de mots
    distincts : seuls les ``max_labels`` mots les plus connectés sont étiquetés,
    pour garder la figure lisible (tous les nœuds restent dessinés)."""
    if G.number_of_nodes() == 0:
        raise ValueError("Graphe vide : aucun mot à dessiner.")

    pos = nx.spring_layout(G, seed=seed)
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

    artiste_noeuds = nx.draw_networkx_nodes(G, pos, node_color=couleur, node_shape="o",
                                             node_size=tailles, edgecolors="white",
                                             linewidths=1.0, ax=ax)

    poids = nx.get_edge_attributes(G, "poids")
    largeurs = [0.5 + 0.6 * poids.get(e, 1) for e in G.edges()]
    artiste_arcs = nx.draw_networkx_edges(G, pos, edge_color=COULEUR_ARC, width=largeurs, ax=ax)
    # networkx place toujours les nœuds au-dessus des arcs (zorder fixe, quel que
    # soit l'ordre d'appel) : dans les cliques denses créées par la co-occurrence
    # par phrase, les nœuds se chevauchent souvent et masquent totalement les
    # arcs entre eux. On force l'ordre inverse pour que les arcs restent visibles.
    artiste_noeuds.set_zorder(1)
    artiste_arcs.set_zorder(2)

    top_mots = sorted(degres, key=degres.get, reverse=True)[:max_labels]
    nx.draw_networkx_labels(G, pos, labels={m: m for m in top_mots}, font_size=8,
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
