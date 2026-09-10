"""Graphes de contenu ("graphes de mots") par couche — niveau 2 de comparaison.

Le niveau 1 (:mod:`webiso.graphs`) compare la topologie des *balises* : quel type
de balise est parent/enfant de quel autre, indépendamment du texte qu'elles
portent. Ce module compare le **texte porté par ces balises** : chaque mot
devient un sommet, et deux mots sont reliés s'ils co-apparaissent dans une même
phrase ("co-occurrence par phrase" — un graphe de mots au sens de Rousseau &
Vazirgiannis, *Graph-of-words for text classification*). Le graphe obtenu est
**non orienté** : la co-occurrence est une relation symétrique, contrairement à
la relation parent→enfant du niveau 1.

Le niveau 2 ne porte que sur les couches **Méta** et **Contenu** — la couche
Structure (div, nav, header...) n'a pas de contenu textuel qui lui soit propre
et en est donc exclue. Le "contenu" comparé réutilise directement les champs
déjà extraits par :mod:`webiso.extraction`, sans nouvelle extraction HTML :

- **Méta**    → colonne ``Valeur`` (titre, description, mots-clés, hrefs...)
- **Contenu** → colonne ``Valeur`` (texte des titres, paragraphes, liens,
  attributs alt...)

Tokenisation volontairement légère (regex + liste de mots vides statique
FR/EN intégrée) : pas de dépendance NLP supplémentaire (spaCy, nltk...), pour
rester cohérent avec le reste du package et ne pas alourdir le déploiement.
"""

import re
from itertools import combinations

import networkx as nx

from .graphs import PALETTES

# Couleur dominante par couche pour les graphes de mots (reprise des palettes
# de niveau 1, pour la continuité visuelle).
COULEUR_MOTS = {
    "meta": PALETTES["meta"]["head"],
    "contenu": PALETTES["contenu"]["h1"],
}

# Liste statique de mots vides FR + EN — volontairement légère (pas de dépendance NLP).
STOPWORDS = frozenset("""
le la les l un une des de du au aux et ou où à en dans sur pour par avec sans
ce cet cette ces qui que quoi dont il elle ils elles nous vous je tu on se sa
son ses leur leurs ne pas plus très être avoir est sont fait faire comme mais
donc or ni car si tout tous toute toutes autre autres même aussi ainsi alors
ici là cela ça celui celle ceux celles votre vos notre nos mon ma mes ton ta
tes lui y non oui bien peu beaucoup entre depuis pendant après avant sous vers
chez the a an and or but if then else of to in on at by for with without is
are was were be been being this that these those it its he she they we you i
my your his her their our as from not no so do does did have has had will
would can could should may might must about into than too very just up down
out over under again further once here there when where why how all any both
each few more most other some such only own same www com http https
""".split())

_RE_MOT = re.compile(r"[^\W\d_]+", re.UNICODE)
_RE_PHRASE = re.compile(r"[.!?;:\n]+")


def tokeniser(texte):
    """Découpe un texte en mots normalisés (minuscules, sans mots vides, len>=2)."""
    if not texte:
        return []
    mots = _RE_MOT.findall(texte.lower())
    return [m for m in mots if len(m) >= 2 and m not in STOPWORDS]


def decouper_phrases(texte):
    """Découpe un texte en phrases (séparateurs de ponctuation forte)."""
    if not texte:
        return []
    return [p.strip() for p in _RE_PHRASE.split(texte) if p.strip()]


def _phrases_depuis_valeurs(valeurs):
    """Convertit une liste de textes bruts en phrases tokenisables (une entrée
    peut elle-même contenir plusieurs phrases)."""
    phrases = []
    for v in valeurs:
        if not v:
            continue
        sous_phrases = decouper_phrases(v) or [v]
        phrases.extend(sous_phrases)
    return phrases


def phrases_meta(meta_list):
    """Phrases de la couche Méta : valeur de chaque entrée (title, meta, link...)."""
    return _phrases_depuis_valeurs(m.get("Valeur") for m in meta_list)


def phrases_contenu(contenu_list):
    """Phrases de la couche Contenu : valeur de chaque entrée (texte visible)."""
    return _phrases_depuis_valeurs(c.get("Valeur") for c in contenu_list)


def construire_graphe_mots(phrases):
    """Construit un graphe de co-occurrence non orienté à partir d'une liste de
    phrases : deux mots sont reliés s'ils apparaissent dans une même phrase. Le
    poids d'un arc compte le nombre de phrases où la paire co-apparaît."""
    G = nx.Graph()
    for phrase in phrases:
        mots = sorted(set(tokeniser(phrase)))
        G.add_nodes_from(mots)
        for m1, m2 in combinations(mots, 2):
            if G.has_edge(m1, m2):
                G[m1][m2]["poids"] += 1
            else:
                G.add_edge(m1, m2, poids=1)
    return G
