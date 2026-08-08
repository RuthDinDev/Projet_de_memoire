"""CLI reproduisant le pipeline du notebook original : 2 URLs → extraction →
graphes NetworkX → test d'isomorphisme VF2."""

import sys

from .pipeline import analyser_site
from .extraction import afficher_metadonnees, afficher_structure, afficher_contenu
from .graphs import PALETTES, afficher_graphe_formel
from .viz import dessiner_graphe, sauver_graphe
from .isomorphism import test_isomorphisme_complet


def main():
    if len(sys.argv) > 2:
        url1, url2 = sys.argv[1], sys.argv[2]
    else:
        url1 = input("URL du site 1 : ").strip() or "https://example.com"
        url2 = input("URL du site 2 : ").strip() or "https://example.org"

    site1 = analyser_site(url1)
    site2 = analyser_site(url2)

    for site in (site1, site2):
        print("\n" + "█" * 60 + f"\n  SITE : {site['url']}\n" + "█" * 60)
        afficher_metadonnees(site["meta_list"])
        afficher_structure(site["struct_list"])
        afficher_contenu(site["contenu_list"])

    for site in (site1, site2):
        print("\n  ── ", site["domaine"])
        afficher_graphe_formel(site["G_meta"], "G_meta")
        afficher_graphe_formel(site["G_struct"], "G_struct")
        afficher_graphe_formel(site["G_contenu"], "G_contenu")

    for site in (site1, site2):
        d = site["domaine"]
        slug = d.replace(".", "_")
        fig_m = dessiner_graphe(site["G_meta"], PALETTES["meta"], f"Méta — {d}")
        fig_s = dessiner_graphe(site["G_struct"], PALETTES["struct"], f"Structure — {d}")
        fig_c = dessiner_graphe(site["G_contenu"], PALETTES["contenu"], f"Contenu — {d}")
        sauver_graphe(fig_m, f"graphe_meta_{slug}.png")
        sauver_graphe(fig_s, f"graphe_struct_{slug}.png")
        sauver_graphe(fig_c, f"graphe_contenu_{slug}.png")

    test_isomorphisme_complet(site1, site2)


if __name__ == "__main__":
    main()
