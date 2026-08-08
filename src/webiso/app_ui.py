"""Interface Streamlit du package webiso.

Frontend web pour le pipeline : 2 URLs → extraction 3 couches → graphes formels
NetworkX → test d'isomorphisme VF2. Lancer via ``webiso-app`` ou
``streamlit run src/webiso/app_ui.py``.
"""

import pandas as pd
import streamlit as st

from webiso.pipeline import analyser_site
from webiso.graphs import PALETTES
from webiso.viz import dessiner_graphe
from webiso.isomorphism import tester_isomorphisme

COUCHES = [
    ("meta", "G_meta", "Méta"),
    ("struct", "G_struct", "Structure"),
    ("contenu", "G_contenu", "Contenu"),
]

st.set_page_config(page_title="webiso — Isomorphisme structurel HTML", layout="wide")

st.title("webiso")
st.caption(
    "Comparaison structurelle de deux sites web — extraction en 3 couches "
    "(méta · structure · contenu) → graphe formel NetworkX → test d'isomorphisme VF2"
)

col_url1, col_url2 = st.columns(2)
url1 = col_url1.text_input("URL du site 1", "https://example.com")
url2 = col_url2.text_input("URL du site 2", "https://example.org")

if st.button("Comparer", type="primary"):
    try:
        with st.spinner(f"Chargement de {url1}..."):
            site1 = analyser_site(url1)
        with st.spinner(f"Chargement de {url2}..."):
            site2 = analyser_site(url2)
    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        st.stop()

    st.session_state["site1"] = site1
    st.session_state["site2"] = site2

if "site1" in st.session_state and "site2" in st.session_state:
    site1 = st.session_state["site1"]
    site2 = st.session_state["site2"]

    st.header("Tableaux d'extraction")
    for site in (site1, site2):
        with st.expander(f"📄 {site['domaine']}"):
            onglet_meta, onglet_struct, onglet_contenu = st.tabs(["Métadonnées", "Structure", "Contenu"])
            onglet_meta.dataframe(pd.DataFrame(site["meta_list"]), width="stretch")
            onglet_struct.dataframe(pd.DataFrame(site["struct_list"]), width="stretch")
            onglet_contenu.dataframe(pd.DataFrame(site["contenu_list"]), width="stretch")

    st.header("Graphes formels (NetworkX)")
    for palette_key, graph_key, titre in COUCHES:
        st.subheader(titre)
        col1, col2 = st.columns(2)
        for col, site in zip((col1, col2), (site1, site2)):
            fig = dessiner_graphe(site[graph_key], PALETTES[palette_key], f"{titre} — {site['domaine']}")
            col.pyplot(fig)

    st.header("Test d'isomorphisme VF2")
    resultats = {}
    for palette_key, graph_key, titre in COUCHES:
        iso, mapping, rapport = tester_isomorphisme(site1[graph_key], site2[graph_key], titre)
        resultats[palette_key] = iso
        with st.expander(f"{'✅' if iso else '❌'} Couche {titre}", expanded=not iso):
            st.code(rapport, language=None)

    iso_global = all(resultats.values())
    st.divider()
    if iso_global:
        st.success("✅ Les deux sites sont ISOMORPHES — même méta, même structure, même contenu.")
    else:
        couches_ko = [titre for palette_key, _, titre in COUCHES if not resultats[palette_key]]
        st.error(f"❌ Les deux sites ne sont PAS isomorphes. Couche(s) en échec : {', '.join(couches_ko)}")
