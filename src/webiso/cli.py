"""CLI reproduisant le pipeline à deux niveaux : 2 URLs (vrai / faux) →
extraction → graphe complet NetworkX (niveau 1) + graphes de mots (niveau 2)
→ tests d'isomorphisme VF2."""

import sys

from .pipeline import analyser_site
from .extraction import afficher_metadonnees, afficher_structure, afficher_contenu
from .graphs import PALETTE_COMPLETE, afficher_graphe_complet
from .textgraph import COULEUR_MOTS
from .viz import dessiner_graphe, dessiner_graphe_mots, sauver_graphe
from .isomorphism import test_isomorphisme_structure, test_isomorphisme_contenu


def main():
    if len(sys.argv) > 2:
        url_vrai, url_faux = sys.argv[1], sys.argv[2]
    else:
        url_vrai = input("URL du site VRAI (référence) : ").strip() or "https://example.com"
        url_faux = input("URL du site FAUX (candidat)  : ").strip() or "https://example.org"

    vrai = analyser_site(url_vrai)
    faux = analyser_site(url_faux)

    for label, site in (("VRAI", vrai), ("FAUX", faux)):
        print("\n" + "█" * 60 + f"\n  {label} : {site['url']}\n" + "█" * 60)
        afficher_metadonnees(site["meta_list"])
        afficher_structure(site["struct_list"])
        afficher_contenu(site["contenu_list"])

    for label, site in (("VRAI", vrai), ("FAUX", faux)):
        print(f"\n  ── {label} —", site["domaine"])
        afficher_graphe_complet(site["G_complet"], "G_complet")

    for label, site in (("vrai", vrai), ("faux", faux)):
        d = site["domaine"]
        slug = d.replace(".", "_")

        fig = dessiner_graphe(site["G_complet"], PALETTE_COMPLETE, f"Structure complète — {d}")
        sauver_graphe(fig, f"graphe_complet_{label}_{slug}.png")

        fig_m = dessiner_graphe_mots(site["G_meta_mots"], COULEUR_MOTS["meta"], f"Mots méta — {d}")
        fig_c = dessiner_graphe_mots(site["G_contenu_mots"], COULEUR_MOTS["contenu"], f"Mots contenu — {d}")
        sauver_graphe(fig_m, f"graphe_meta_mots_{label}_{slug}.png")
        sauver_graphe(fig_c, f"graphe_contenu_mots_{label}_{slug}.png")

    test_isomorphisme_structure(vrai, faux)
    test_isomorphisme_contenu(vrai, faux)


if __name__ == "__main__":
    main()
