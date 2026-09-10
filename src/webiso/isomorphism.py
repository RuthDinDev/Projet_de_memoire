"""Test d'isomorphisme structurel (VF2) via ``networkx.algorithms.isomorphism``.

Deux niveaux de comparaison, chacun avec son propre test VF2, entre un site
« vrai » (référence) et un site « faux » (candidat) — labels génériques : la
comparaison reste symétrique, ce sont deux sites quelconques à comparer.

- **Niveau 1** (``tester_isomorphisme`` / ``test_isomorphisme_structure``) :
  porte sur la topologie d'**un seul graphe complet et non segmenté** par site
  (:mod:`webiso.graphs`, orienté, parent→enfant, tout l'arbre DOM). Les deux
  sites sont isomorphes si un renommage des sommets de l'un donne exactement
  l'autre, indépendamment des balises HTML portées par chaque sommet.
- **Niveau 2** (``tester_isomorphisme_mots`` / ``test_isomorphisme_contenu``) :
  porte sur la topologie des graphes de *mots* (:mod:`webiso.textgraph`, non
  orientés, co-occurrence), pour les couches Méta et Contenu uniquement. Comme
  deux pages distinctes ont presque toujours un vocabulaire de taille
  différente, ce test conclut le plus souvent à la non-isomorphie dès
  l'invariant |S1|≠|S2| — c'est attendu : il mesure une identité de contenu
  stricte, pas une simple similarité.

Les deux niveaux sont rapportés séparément (pas de verdict combiné unique) : la
question « même structure ? » et la question « même contenu ? » sont deux
questions distinctes.
"""

from networkx.algorithms.isomorphism import DiGraphMatcher, GraphMatcher

# Au-delà de ce nombre de mots communs, VF2 sur un graphe non orienté devient
# coûteux ; on court-circuite avec un constat plutôt que de bloquer l'interface.
SEUIL_TAILLE_VF2_MOTS = 150

# Couches de contenu comparées au niveau 2 (Structure exclue : ses balises
# n'ont pas de contenu propre, voir webiso.textgraph.phrases_struct).
COUCHES_NIVEAU2 = (("meta", "Méta"), ("contenu", "Contenu"))


def tester_isomorphisme(G1, G2, label=""):
    """
    VF2 (NetworkX) — Cordella et al., IEEE TPAMI 2004.
    Retourne (bool, mapping|None, rapport_str)
    """
    rap = [f"  VF2 (NetworkX) [{label}]", "  " + "─" * 52]
    n1, n2 = G1.number_of_nodes(), G2.number_of_nodes()
    a1, a2 = G1.number_of_edges(), G2.number_of_edges()
    rap.append(f"  |S1|={n1}  |S2|={n2}  |A1|={a1}  |A2|={a2}")

    if n1 != n2:
        rap.append("  ✗  |S1|≠|S2| → NON isomorphes")
        return False, None, "\n".join(rap)
    if a1 != a2:
        rap.append("  ✗  |A1|≠|A2| → NON isomorphes")
        return False, None, "\n".join(rap)

    rap.append("  ✓  Invariants OK — recherche VF2 (DiGraphMatcher)...")
    matcher = DiGraphMatcher(G1, G2)
    est_iso = matcher.is_isomorphic()

    if not est_iso:
        rap.append("  ✗  NON ISOMORPHES")
        return False, None, "\n".join(rap)

    mapping = dict(matcher.mapping)
    rap.append("  ✓  ISOMORPHES — mapping :")
    for u, v in mapping.items():
        rap.append(f"    {u:<22} →  {v}")
    return True, mapping, "\n".join(rap)


def test_isomorphisme_structure(vrai, faux):
    """
    Niveau 1 : isomorphisme du graphe complet et non segmenté (tout l'arbre DOM).
    Retourne (bool, mapping|None, rapport_str)
    """
    print("\n" + "═" * 60)
    print("  NIVEAU 1 — ISOMORPHISME DE LA STRUCTURE  (VF2/NetworkX — graphe complet)")
    print(f"  Vrai : {vrai['url']}")
    print(f"  Faux : {faux['url']}")
    print("═" * 60)

    iso, mapping, rap = tester_isomorphisme(vrai["G_complet"], faux["G_complet"], "Structure complète")
    print(rap)

    print("\n" + "═" * 60)
    print("  VERDICT NIVEAU 1 (structure)")
    print("  " + "─" * 56)
    if iso:
        print("  ✅  STRUCTURES ISOMORPHES — même arbre de balises.")
    else:
        print("  ❌  STRUCTURES NON ISOMORPHES.")
    print("═" * 60)

    return iso, mapping, rap


def tester_isomorphisme_mots(G1, G2, label=""):
    """
    VF2 (NetworkX) sur graphes non orientés (co-occurrence de mots) — niveau 2.
    Retourne (bool, mapping|None, rapport_str)
    """
    rap = [f"  VF2 mots (NetworkX) [{label}]", "  " + "─" * 52]
    n1, n2 = G1.number_of_nodes(), G2.number_of_nodes()
    a1, a2 = G1.number_of_edges(), G2.number_of_edges()
    rap.append(f"  |S1|={n1}  |S2|={n2}  |A1|={a1}  |A2|={a2}")

    if n1 != n2:
        rap.append("  ✗  |S1|≠|S2| → NON isomorphes (vocabulaires de tailles différentes)")
        return False, None, "\n".join(rap)
    if a1 != a2:
        rap.append("  ✗  |A1|≠|A2| → NON isomorphes")
        return False, None, "\n".join(rap)
    if n1 > SEUIL_TAILLE_VF2_MOTS:
        rap.append(f"  ⚠  |S1|=|S2|={n1} > {SEUIL_TAILLE_VF2_MOTS} → test VF2 exact trop coûteux, ignoré")
        rap.append("     (invariants de taille identiques, mais isomorphie non vérifiée)")
        return False, None, "\n".join(rap)

    rap.append("  ✓  Invariants OK — recherche VF2 (GraphMatcher, non orienté)...")
    matcher = GraphMatcher(G1, G2)
    est_iso = matcher.is_isomorphic()

    if not est_iso:
        rap.append("  ✗  NON ISOMORPHES")
        return False, None, "\n".join(rap)

    mapping = dict(matcher.mapping)
    rap.append("  ✓  ISOMORPHES — mapping (mot vrai → mot faux) :")
    for u, v in mapping.items():
        rap.append(f"    {u:<22} →  {v}")
    return True, mapping, "\n".join(rap)


def test_isomorphisme_contenu(vrai, faux):
    """
    Niveau 2 : isomorphisme des graphes de co-occurrence de mots, pour les
    couches Méta et Contenu (contenu des balises de métadonnées, puis contenu
    des balises de contenu — la couche Structure n'a pas de contenu propre).
    Retourne (bool_global, résultats_par_couche)
    """
    print("\n" + "═" * 60)
    print("  NIVEAU 2 — ISOMORPHISME DU CONTENU DES BALISES  (VF2/NetworkX — Méta & Contenu)")
    print(f"  Vrai : {vrai['url']}")
    print(f"  Faux : {faux['url']}")
    print("═" * 60)

    resultats = {}
    for cle, titre in COUCHES_NIVEAU2:
        print(f"\n  ┌── Contenu couche {titre}")
        iso, mapping, rap = tester_isomorphisme_mots(
            vrai[f"G_{cle}_mots"], faux[f"G_{cle}_mots"], titre)
        print(rap)
        resultats[cle] = {"iso": iso, "mapping": mapping}
        print(f"  └── Résultat : {'✓ ISOMORPHE' if iso else '✗ NON ISOMORPHE'}")

    iso_global = all(r["iso"] for r in resultats.values())
    print("\n" + "═" * 60)
    print("  VERDICT NIVEAU 2 (contenu)")
    print("  " + "─" * 56)
    for cle, titre in COUCHES_NIVEAU2:
        print(f"  {titre:<10}: {'✓' if resultats[cle]['iso'] else '✗'}")
    print("  " + "─" * 56)
    if iso_global:
        print("  ✅  CONTENUS ISOMORPHES (Méta & Contenu)")
    else:
        couches_ko = [titre for cle, titre in COUCHES_NIVEAU2 if not resultats[cle]["iso"]]
        print("  ❌  CONTENUS NON ISOMORPHES")
        print(f"      Couche(s) non isomorphe(s) : {', '.join(couches_ko)}")
    print("═" * 60)

    return iso_global, resultats
