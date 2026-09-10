"""Exemple d'utilisation programmatique du package webiso (équivalent au notebook)."""

from webiso import (
    analyser_site,
    afficher_metadonnees, afficher_structure, afficher_contenu,
    afficher_graphe_complet, PALETTE_COMPLETE,
    dessiner_graphe, dessiner_graphe_mots, sauver_graphe,
    COULEUR_MOTS,
    test_isomorphisme_structure, test_isomorphisme_contenu,
)

url_vrai = "https://arxiv.org/abs/2408.10954"
url_faux = "https://www.wikipedia.org/"

vrai = analyser_site(url_vrai)
faux = analyser_site(url_faux)

afficher_metadonnees(vrai["meta_list"])
afficher_structure(vrai["struct_list"])
afficher_contenu(vrai["contenu_list"])

# Niveau 1 — structure complète (un seul graphe non segmenté)
afficher_graphe_complet(vrai["G_complet"], "G_complet_vrai")

fig = dessiner_graphe(vrai["G_complet"], PALETTE_COMPLETE, f"Structure complète — {vrai['domaine']}")
sauver_graphe(fig, "structure_vrai.png")

iso_structure, mapping, rapport = test_isomorphisme_structure(vrai, faux)
print("Structure isomorphe ?", iso_structure)

# Niveau 2 — contenu des balises Méta et Contenu (graphes de mots)
fig_mots = dessiner_graphe_mots(vrai["G_contenu_mots"], COULEUR_MOTS["contenu"],
                                 f"Mots contenu — {vrai['domaine']}")
sauver_graphe(fig_mots, "mots_contenu_vrai.png")

iso_contenu, resultats_contenu = test_isomorphisme_contenu(vrai, faux)
print("Contenu isomorphe ?", iso_contenu)
