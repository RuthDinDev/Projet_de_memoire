"""webiso — extraction structurelle HTML, graphes NetworkX, isomorphisme VF2.

Pipeline à deux niveaux, entre un site « vrai » (référence) et un site « faux »
(candidat) — labels génériques, la comparaison reste symétrique :
  - niveau 1 : UN graphe complet et non segmenté par site, sur tout l'arbre DOM
    (orienté) → VF2 orienté ;
  - niveau 2 : graphes de mots (contenu des couches Méta et Contenu, non
    orientés, co-occurrence) → VF2 non orienté.
"""

from .utils import tronquer, nettoyer, afficher_tableau
from .fetch import valider_url, charger_page
from .extraction import (
    BALISES_META, BALISES_STRUCT, BALISES_CONTENU,
    extraire_metadonnees, afficher_metadonnees,
    extraire_structure, afficher_structure,
    extraire_contenu, afficher_contenu,
)
from .graphs import PALETTES, PALETTE_COMPLETE, construire_graphe_complet, afficher_graphe_complet
from .textgraph import (
    COULEUR_MOTS, tokeniser, decouper_phrases,
    phrases_meta, phrases_contenu, construire_graphe_mots,
)
from .viz import dessiner_graphe, dessiner_graphe_mots, sauver_graphe, afficher_graphe
from .isomorphism import (
    tester_isomorphisme, test_isomorphisme_structure,
    tester_isomorphisme_mots, test_isomorphisme_contenu,
)
from .pipeline import analyser_site

__version__ = "0.2.0"

__all__ = [
    "tronquer", "nettoyer", "afficher_tableau",
    "valider_url", "charger_page",
    "BALISES_META", "BALISES_STRUCT", "BALISES_CONTENU",
    "extraire_metadonnees", "afficher_metadonnees",
    "extraire_structure", "afficher_structure",
    "extraire_contenu", "afficher_contenu",
    "PALETTES", "PALETTE_COMPLETE", "construire_graphe_complet", "afficher_graphe_complet",
    "COULEUR_MOTS", "tokeniser", "decouper_phrases",
    "phrases_meta", "phrases_contenu", "construire_graphe_mots",
    "dessiner_graphe", "dessiner_graphe_mots", "sauver_graphe", "afficher_graphe",
    "tester_isomorphisme", "test_isomorphisme_structure",
    "tester_isomorphisme_mots", "test_isomorphisme_contenu",
    "analyser_site",
]
