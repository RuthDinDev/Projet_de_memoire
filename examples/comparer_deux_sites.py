"""Exemple d'utilisation programmatique du package webiso (équivalent au notebook)."""

from webiso import (
    analyser_site,
    afficher_metadonnees, afficher_structure, afficher_contenu,
    afficher_graphe_formel, PALETTES,
    dessiner_graphe, sauver_graphe,
    test_isomorphisme_complet,
)

url1 = "https://arxiv.org/abs/2408.10954"
url2 = "https://www.wikipedia.org/"

site1 = analyser_site(url1)
site2 = analyser_site(url2)

afficher_metadonnees(site1["meta_list"])
afficher_structure(site1["struct_list"])
afficher_contenu(site1["contenu_list"])

afficher_graphe_formel(site1["G_meta"], "G_meta1")

fig = dessiner_graphe(site1["G_struct"], PALETTES["struct"], f"Structure — {site1['domaine']}")
sauver_graphe(fig, "structure_site1.png")

iso_global, resultats = test_isomorphisme_complet(site1, site2)
print("Isomorphes ?", iso_global)
