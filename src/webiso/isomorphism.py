"""Test d'isomorphisme structurel (VF2) via ``networkx.algorithms.isomorphism``.

Le test porte uniquement sur la topologie des graphes (sommets + arcs), pas sur les
étiquettes ``tag`` — deux couches sont isomorphes si un renommage des sommets de
l'une donne exactement l'autre, indépendamment des balises HTML portées par chaque
sommet (cohérent avec le comportement du VF2 original du mémoire).
"""

from networkx.algorithms.isomorphism import DiGraphMatcher


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


def test_isomorphisme_complet(site1, site2):
    """
    Teste l'isomorphisme sur les 3 couches indépendamment.
    Retourne (bool_global, résultats_par_couche)
    """
    print("\n" + "═" * 60)
    print("  TEST D'ISOMORPHISME COMPLET  (VF2/NetworkX — 3 couches)")
    print(f"  Site 1 : {site1['url']}")
    print(f"  Site 2 : {site2['url']}")
    print("═" * 60)

    resultats = {}

    print("\n  ┌── Couche 1 : MÉTADONNÉES")
    iso_m, map_m, rap_m = tester_isomorphisme(site1["G_meta"], site2["G_meta"], "Méta")
    print(rap_m)
    resultats["meta"] = {"iso": iso_m, "mapping": map_m}
    print(f"  └── Résultat méta     : {'✓ ISOMORPHE' if iso_m else '✗ NON ISOMORPHE'}")

    print("\n  ┌── Couche 2 : STRUCTURE")
    iso_s, map_s, rap_s = tester_isomorphisme(site1["G_struct"], site2["G_struct"], "Structure")
    print(rap_s)
    resultats["struct"] = {"iso": iso_s, "mapping": map_s}
    print(f"  └── Résultat structure : {'✓ ISOMORPHE' if iso_s else '✗ NON ISOMORPHE'}")

    print("\n  ┌── Couche 3 : CONTENU")
    iso_c, map_c, rap_c = tester_isomorphisme(site1["G_contenu"], site2["G_contenu"], "Contenu")
    print(rap_c)
    resultats["contenu"] = {"iso": iso_c, "mapping": map_c}
    print(f"  └── Résultat contenu   : {'✓ ISOMORPHE' if iso_c else '✗ NON ISOMORPHE'}")

    iso_global = iso_m and iso_s and iso_c
    print("\n" + "═" * 60)
    print("  VERDICT FINAL")
    print("  " + "─" * 56)
    print(f"  Méta     : {'✓' if iso_m else '✗'}")
    print(f"  Structure: {'✓' if iso_s else '✗'}")
    print(f"  Contenu  : {'✓' if iso_c else '✗'}")
    print("  " + "─" * 56)
    if iso_global:
        print("   LES DEUX SITES SONT ISOMORPHES")
        print("      Même méta, même structure, même contenu.")
    else:
        couches_ko = [c for c, r in resultats.items() if not r["iso"]]
        print("   LES DEUX SITES NE SONT PAS ISOMORPHES")
        print(f"      Couche(s) non isomorphe(s) : {', '.join(couches_ko)}")
    print("═" * 60)

    return iso_global, resultats
