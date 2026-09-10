"""Pipeline complet : URL → HTML → graphes NetworkX (niveau 1 : graphe complet
et non segmenté de toutes les balises ; niveau 2 : graphes de mots pour le
contenu des couches Méta et Contenu)."""

from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .fetch import valider_url, charger_page
from .extraction import extraire_metadonnees, extraire_structure, extraire_contenu
from .graphs import construire_graphe_complet
from .textgraph import phrases_meta, phrases_contenu, construire_graphe_mots


def analyser_site(url):
    """
    Charge une page et extrait les 3 couches (pour les tableaux d'affichage).
    Retourne un dict avec :
      - le graphe complet et non segmenté de toutes les balises (niveau 1,
        ``G_complet``, ``networkx.DiGraph``) ;
      - les graphes de mots des couches Méta et Contenu (niveau 2,
        ``G_meta_mots``/``G_contenu_mots``, ``networkx.Graph``).
    """
    url = valider_url(url)
    print(f"\n  ⏳  Chargement : {url}")
    html = charger_page(url)
    soup = BeautifulSoup(html, "html.parser")
    print(f"  ✓  {len(html):,} car.")
    domaine = urlparse(url).netloc or url

    meta_list, _ = extraire_metadonnees(soup)
    struct_list, _ = extraire_structure(soup)
    contenu_list, _ = extraire_contenu(soup, url)

    G_complet = construire_graphe_complet(soup)
    print(f"  Graphe complet : {G_complet.number_of_nodes()} nœuds   {G_complet.number_of_edges()} arcs")

    G_meta_mots = construire_graphe_mots(phrases_meta(meta_list))
    G_contenu_mots = construire_graphe_mots(phrases_contenu(contenu_list))
    print(f"  Mots méta      : {G_meta_mots.number_of_nodes()} mots   {G_meta_mots.number_of_edges()} liens")
    print(f"  Mots contenu   : {G_contenu_mots.number_of_nodes()} mots {G_contenu_mots.number_of_edges()} liens")

    return {
        "url": url, "domaine": domaine, "soup": soup,
        "meta_list": meta_list, "struct_list": struct_list, "contenu_list": contenu_list,
        "G_complet": G_complet,
        "G_meta_mots": G_meta_mots, "G_contenu_mots": G_contenu_mots,
    }
