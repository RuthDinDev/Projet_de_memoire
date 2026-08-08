"""webiso — extraction structurelle HTML, graphes NetworkX, isomorphisme VF2.

Pipeline : 2 URLs → extraction par couche (méta / structure / contenu)
→ graphe formel NetworkX par couche → visualisation → test d'isomorphisme VF2 × 3
→ verdict global.
"""

from .utils import tronquer, nettoyer, afficher_tableau
from .fetch import valider_url, charger_page
from .extraction import (
    BALISES_META, BALISES_STRUCT, BALISES_CONTENU,
    extraire_metadonnees, afficher_metadonnees,
    extraire_structure, afficher_structure,
    extraire_contenu, afficher_contenu,
)
from .graphs import PALETTES, construire_graphe_formel, afficher_graphe_formel
from .viz import dessiner_graphe, sauver_graphe, afficher_graphe
from .isomorphism import tester_isomorphisme, test_isomorphisme_complet
from .pipeline import analyser_site

__version__ = "0.1.0"

__all__ = [
    "tronquer", "nettoyer", "afficher_tableau",
    "valider_url", "charger_page",
    "BALISES_META", "BALISES_STRUCT", "BALISES_CONTENU",
    "extraire_metadonnees", "afficher_metadonnees",
    "extraire_structure", "afficher_structure",
    "extraire_contenu", "afficher_contenu",
    "PALETTES", "construire_graphe_formel", "afficher_graphe_formel",
    "dessiner_graphe", "sauver_graphe", "afficher_graphe",
    "tester_isomorphisme", "test_isomorphisme_complet",
    "analyser_site",
]
