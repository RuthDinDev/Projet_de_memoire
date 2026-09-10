"""Construction du graphe complet de balises (Niveau 1), sous forme de
``networkx.DiGraph``.

Contrairement à une première version qui segmentait le Niveau 1 en 3 graphes
(méta / structure / contenu), ce module construit **un seul graphe complet et
non segmenté** par site : chaque balise du document (sans filtrage par couche
ni par liste de balises) devient un sommet, et un arc relie chaque balise à son
véritable parent DOM. C'est donc l'arbre HTML entier de la page, tel quel.
"""

from collections import defaultdict

import networkx as nx

# Palettes de couleurs par couche sémantique (clé = tag HTML, valeur = couleur hex)
# — conservées pour le Niveau 2 (webiso.textgraph.COULEUR_MOTS) et pour colorer
# le graphe complet du Niveau 1 de façon cohérente avec les couches d'origine.
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

# Palette unique pour le graphe complet : union des 3 palettes ci-dessus. Toute
# balise absente (svg, iframe, input...) retombe sur COULEUR_DEFAUT (webiso.viz).
PALETTE_COMPLETE = {**PALETTES["meta"], **PALETTES["struct"], **PALETTES["contenu"]}


def construire_graphe_complet(soup):
    """Construit un graphe orienté complet et non segmenté représentant tout
    l'arbre DOM de la page : chaque balise est un sommet (uid rendu unique,
    ex. ``div``, ``div_2``...), chaque arc relie une balise à son véritable
    parent DOM. Aucun filtrage par couche ni par liste de balises."""
    G = nx.DiGraph()
    compteur = defaultdict(int)

    def uid_pour(tag_name):
        compteur[tag_name] += 1
        c = compteur[tag_name]
        return tag_name if c == 1 else f"{tag_name}_{c}"

    def parcourir(el, parent_uid, depth):
        for enfant in getattr(el, "children", []):
            nom = getattr(enfant, "name", None)
            if nom is None:
                continue  # texte ou commentaire : pas une balise
            uid = uid_pour(nom)
            G.add_node(uid, tag=nom, depth=depth)
            if parent_uid is not None:
                G.add_edge(parent_uid, uid)
            parcourir(enfant, uid, depth + 1)

    parcourir(soup, None, 0)
    return G


def afficher_graphe_complet(G, label="G"):
    print(f"\n  {label} = (S, A)  —  graphe complet, non segmenté")
    print(f"  |S| = {G.number_of_nodes()} sommets   |A| = {G.number_of_edges()} arcs")
    print("  S :")
    for uid, data in G.nodes(data=True):
        print(f"    {uid:<22} depth={data['depth']}  deg_in={G.in_degree(uid)}  deg_out={G.out_degree(uid)}")
    print("  A :")
    for u, v in G.edges():
        print(f"    {u:<22} →  {v}")
