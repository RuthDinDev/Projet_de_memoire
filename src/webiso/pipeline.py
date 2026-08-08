"""Pipeline complet : URL → HTML → 3 couches extraites → 3 graphes formels NetworkX."""

from urllib.parse import urlparse

from bs4 import BeautifulSoup

from .fetch import valider_url, charger_page
from .extraction import extraire_metadonnees, extraire_structure, extraire_contenu
from .graphs import construire_graphe_formel


def analyser_site(url):
    """
    Charge une page et extrait les 3 couches.
    Retourne un dict avec toutes les données et les 3 graphes formels (networkx.DiGraph).
    """
    url = valider_url(url)
    print(f"\n  ⏳  Chargement : {url}")
    html = charger_page(url)
    soup = BeautifulSoup(html, "html.parser")
    print(f"  ✓  {len(html):,} car.")
    domaine = urlparse(url).netloc or url

    meta_list, noeuds_meta = extraire_metadonnees(soup)
    struct_list, noeuds_struct = extraire_structure(soup)
    contenu_list, noeuds_contenu = extraire_contenu(soup, url)

    G_meta = construire_graphe_formel(noeuds_meta)
    G_struct = construire_graphe_formel(noeuds_struct)
    G_contenu = construire_graphe_formel(noeuds_contenu)

    print(f"  Couche méta    : {len(noeuds_meta)} nœuds   {G_meta.number_of_edges()} arcs")
    print(f"  Couche struct  : {len(noeuds_struct)} nœuds  {G_struct.number_of_edges()} arcs")
    print(f"  Couche contenu : {len(noeuds_contenu)} nœuds {G_contenu.number_of_edges()} arcs")

    return {
        "url": url, "domaine": domaine, "soup": soup,
        "meta_list": meta_list, "noeuds_meta": noeuds_meta, "G_meta": G_meta,
        "struct_list": struct_list, "noeuds_struct": noeuds_struct, "G_struct": G_struct,
        "contenu_list": contenu_list, "noeuds_contenu": noeuds_contenu, "G_contenu": G_contenu,
    }
