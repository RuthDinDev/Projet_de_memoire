"""Interface Streamlit du package webiso.

Frontend web pour le pipeline à deux niveaux :
  2 URLs (vrai / faux) → extraction 3 couches →
  (niveau 1) UN graphe complet et non segmenté par site → VF2 orienté ;
  (niveau 2) graphes de mots pour Méta et Contenu → VF2 non orienté.
Lancer via ``webiso-app`` ou ``streamlit run src/webiso/app_ui.py``.
"""

import pandas as pd
import streamlit as st

from webiso.pipeline import analyser_site
from webiso.graphs import PALETTE_COMPLETE
from webiso.textgraph import COULEUR_MOTS
from webiso.viz import dessiner_graphe, dessiner_graphe_mots
from webiso.isomorphism import tester_isomorphisme, tester_isomorphisme_mots, COUCHES_NIVEAU2

st.set_page_config(page_title="webiso — Isomorphisme structurel HTML", layout="wide")

st.title("webiso")
st.caption(
    "Comparaison structurelle d'un site 1 (référence) et d'un site 2 "
    "(candidat), à deux niveaux : (1) la structure complète du DOM, "
    "(2) le contenu porté par les balises Méta et Contenu (mots et leurs "
    "co-occurrences)."
)

col_url1, col_url2 = st.columns(2)
url_vrai = col_url1.text_input("URL du site 1(référence)", "https://example.com")
url_faux = col_url2.text_input("URL du site 2(candidat)", "https://example.org")

if st.button("Comparer", type="primary"):
    try:
        with st.spinner(f"Chargement de {url_vrai}..."):
            vrai = analyser_site(url_vrai)
        with st.spinner(f"Chargement de {url_faux}..."):
            faux = analyser_site(url_faux)
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        st.stop()

    st.session_state["vrai"] = vrai
    st.session_state["faux"] = faux

if "vrai" in st.session_state and "faux" in st.session_state:
    vrai = st.session_state["vrai"]
    faux = st.session_state["faux"]

    st.header("Tableaux d'extraction")
    for label, site in (("VRAI", vrai), ("FAUX", faux)):
        with st.expander(f"📄 {label} — {site['domaine']}"):
            onglet_meta, onglet_struct, onglet_contenu = st.tabs(["Métadonnées", "Structure", "Contenu"])
            onglet_meta.dataframe(pd.DataFrame(site["meta_list"]), width="stretch")
            onglet_struct.dataframe(pd.DataFrame(site["struct_list"]), width="stretch")
            onglet_contenu.dataframe(pd.DataFrame(site["contenu_list"]), width="stretch")

    # ── NIVEAU 1 — structure complète ─────────────────────────────────
    st.header("Niveau 1 — Structure complète (graphe non segmenté)")
    st.caption("Un seul graphe par site, sur tout l'arbre DOM (orienté, parent → enfant).")

    col1, col2 = st.columns(2)
    fig_vrai = dessiner_graphe(vrai["G_complet"], PALETTE_COMPLETE, f"VRAI — {vrai['domaine']}")
    fig_faux = dessiner_graphe(faux["G_complet"], PALETTE_COMPLETE, f"FAUX — {faux['domaine']}")
    col1.pyplot(fig_vrai)
    col2.pyplot(fig_faux)

    st.subheader("Test d'isomorphisme VF2 — structure")
    iso_n1, mapping_n1, rapport_n1 = tester_isomorphisme(
        vrai["G_complet"], faux["G_complet"], "Structure complète")
    with st.expander(f"{'✅' if iso_n1 else '❌'} Rapport détaillé", expanded=not iso_n1):
        st.code(rapport_n1, language=None)

    st.divider()
    if iso_n1:
        st.success("✅ Structures ISOMORPHES — même arbre de balises.")
    else:
        st.error("❌ Structures NON isomorphes.")

    # ── NIVEAU 2 — contenu des balises (Méta & Contenu) ───────────────
    st.header("Niveau 2 — Contenu des balises (Méta & Contenu)")
    st.caption(
        "Graphes de co-occurrence de mots (non orientés) : deux mots sont reliés "
        "s'ils apparaissent dans une même phrase du contenu de la couche. La "
        "couche Structure n'a pas de contenu textuel propre et n'est donc pas "
        "comparée ici. Deux pages différentes ont presque toujours un "
        "vocabulaire de taille différente — un verdict « non isomorphe » ici "
        "est donc attendu la plupart du temps ; c'est un test d'identité "
        "stricte du contenu, pas de simple similarité."
    )

    for cle, titre in COUCHES_NIVEAU2:
        st.subheader(f"Mots — {titre}")
        col1, col2 = st.columns(2)
        col1.pyplot(dessiner_graphe_mots(vrai[f"G_{cle}_mots"], COULEUR_MOTS[cle], f"VRAI — {titre} — {vrai['domaine']}"))
        col2.pyplot(dessiner_graphe_mots(faux[f"G_{cle}_mots"], COULEUR_MOTS[cle], f"FAUX — {titre} — {faux['domaine']}"))

    st.subheader("Test d'isomorphisme VF2 — contenu")
    resultats_n2 = {}
    for cle, titre in COUCHES_NIVEAU2:
        iso, mapping, rapport = tester_isomorphisme_mots(
            vrai[f"G_{cle}_mots"], faux[f"G_{cle}_mots"], titre)
        resultats_n2[cle] = iso
        with st.expander(f"{'✅' if iso else '❌'} Contenu {titre}", expanded=False):
            st.code(rapport, language=None)

    iso_global_n2 = all(resultats_n2.values())
    st.divider()
    if iso_global_n2:
        st.success("✅ Contenus ISOMORPHES (Méta & Contenu).")
    else:
        couches_ko = [titre for cle, titre in COUCHES_NIVEAU2 if not resultats_n2[cle]]
        st.info(f"ℹ️ Contenus non isomorphes. Couche(s) différente(s) : {', '.join(couches_ko)}")
