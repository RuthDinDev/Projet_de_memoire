"""Construction du graphe formel G=(S,A) d'une couche, sous forme de ``networkx.DiGraph``.

Chaque nœud hiérarchique ``{"tag", "depth", ...}`` produit un sommet identifié par un
UID unique (``div``, ``div_2``, ``div_3``, ...) et porte les attributs ``tag`` et
``depth``. Un arc relie chaque nœud à son plus proche ancestor de profondeur inférieure
encore ouvert (pile par profondeur), exactement comme dans l'algorithme original.
"""

from collections import defaultdict

import networkx as nx

# Palettes de couleurs par couche sémantique (clé = tag HTML, valeur = couleur hex)
PALETTES = {
    "meta": {"head": "#7F77DD", "title": "#AFA9EC", "meta": "#CECBF6",
              "link": "#B5ACF2", "script": "#9D94EE", "style": "#C8C2F4", "base": "#DDD9FC"},
    "struct": {"body": "#2D6FA3", "header": "#378ADD", "nav": "#4A9AE8",
               "main": "#5DADF5", "section": "#1D9E75", "article": "#27B885",
               "aside": "#5DCAA5", "footer": "#0A6B4E", "div": "#7BCFB5",
               "ul": "#639922", "ol": "#7AB52E", "li": "#97C459", "form": "#D85A30"},
    "contenu": {"h1": "#BA7517", "h2": "#D4881A", "h3": "#EF9F27", "h4": "#FAB84A",
                "h5": "#FAC775", "h6": "#FAD99E", "p": "#5D8AA8", "a": "#3A7CA5",
                "img": "#E07B54", "figure": "#D4956A", "figcaption": "#DEAF87",
                "table": "#7B68EE", "thead": "#9381F0", "tbody": "#AFA0F5",
                "tr": "#C4B8FA", "td": "#D8D0FD", "th": "#C0B5FB",
                "blockquote": "#B5A642", "pre": "#8B8B6B", "code": "#A0A078",
                "em": "#88AACC", "strong": "#4477AA", "span": "#AABBCC"},
}


def construire_graphe_formel(noeuds):
    """Construit G=(S,A) à partir d'une liste de nœuds hiérarchiques et retourne un
    ``networkx.DiGraph`` : sommets = uid (tag rendu unique), attributs = tag/depth,
    arcs = parent → enfant."""
    G = nx.DiGraph()
    compteur = defaultdict(int)
    pile = {}

    for n in noeuds:
        compteur[n["tag"]] += 1
        c = compteur[n["tag"]]
        uid = n["tag"] if c == 1 else f"{n['tag']}_{c}"
        depth = n["depth"]

        G.add_node(uid, tag=n["tag"], depth=depth)
        if depth > 0 and (depth - 1) in pile:
            G.add_edge(pile[depth - 1], uid)
        pile[depth] = uid
        for k in [k for k in pile if k > depth]:
            del pile[k]

    return G


def afficher_graphe_formel(G, label="G"):
    print(f"\n  {label} = (S, A)")
    print(f"  |S| = {G.number_of_nodes()} sommets   |A| = {G.number_of_edges()} arcs")
    print("  S :")
    for uid, data in G.nodes(data=True):
        print(f"    {uid:<22} depth={data['depth']}  deg_in={G.in_degree(uid)}  deg_out={G.out_degree(uid)}")
    print("  A :")
    for u, v in G.edges():
        print(f"    {u:<22} →  {v}")
