"""Extraction des 3 couches d'une page HTML : métadonnées, structure, contenu.

Chaque fonction ``extraire_*`` retourne un couple :
  - une liste de dicts pour l'affichage tabulaire ;
  - une liste de « nœuds » hiérarchiques ``{"tag", "depth", "parent_tag", "index"}``
    consommée ensuite par :mod:`webiso.graphs` pour construire le graphe formel.
"""

from .utils import tronquer, nettoyer, afficher_tableau

# ══════════════════════════════════════════════════════════════════════
# EXTRACTION 1 — MÉTADONNÉES
# Balises : <head> <title> <meta> <link> <script> <style> <base>
# ══════════════════════════════════════════════════════════════════════

BALISES_META = ["head", "title", "meta", "link", "script", "style", "base"]


def extraire_metadonnees(soup):
    """
    Extrait les métadonnées du <head> :
      - title, meta (name/property/charset), link (rel), script, style
    Retourne : liste de dicts + liste de noeuds hiérarchiques
    """
    meta_list = []
    head = soup.find("head")
    if not head:
        return [], []

    t = head.find("title")
    if t:
        meta_list.append({"Type": "title", "Attribut": "—", "Valeur": tronquer(t.get_text(strip=True), 60)})

    for m in head.find_all("meta"):
        name = m.get("name") or m.get("property") or m.get("http-equiv") or "charset" if m.get("charset") else "—"
        val = m.get("content") or m.get("charset") or "—"
        meta_list.append({"Type": "meta", "Attribut": tronquer(str(name), 24), "Valeur": tronquer(str(val), 60)})

    for l in head.find_all("link"):
        meta_list.append({"Type": "link", "Attribut": tronquer(l.get("rel", ["—"])[0], 24),
                           "Valeur": tronquer(l.get("href", "—"), 60)})

    for s in head.find_all("script"):
        src = s.get("src", "(inline)")
        meta_list.append({"Type": "script", "Attribut": "src", "Valeur": tronquer(src, 60)})

    for s in head.find_all("style"):
        meta_list.append({"Type": "style", "Attribut": "(inline)", "Valeur": "—"})

    noeuds = []
    vus = set()

    def parcourir(el, depth=0, parent="racine"):
        nom = getattr(el, "name", None)
        if nom is None or nom not in BALISES_META:
            for e in getattr(el, "children", []):
                parcourir(e, depth, parent)
            return
        cle = (nom, depth, parent)
        if cle not in vus:
            vus.add(cle)
            noeuds.append({"tag": nom, "depth": depth, "parent_tag": parent, "index": len(noeuds)})
        for e in el.children:
            parcourir(e, depth + 1, nom)

    parcourir(head)
    return meta_list, noeuds


def afficher_metadonnees(meta_list):
    afficher_tableau(
        "MÉTADONNÉES (<head>)",
        ["Type", "Attribut", "Valeur"], [8, 26, 62],
        [[m["Type"], m["Attribut"], m["Valeur"]] for m in meta_list])


# ══════════════════════════════════════════════════════════════════════
# EXTRACTION 2 — STRUCTURE
# Balises : <body> <header> <nav> <main> <section> <article>
#           <aside> <footer> <div> <ul> <ol> <li> <form>
# ══════════════════════════════════════════════════════════════════════

BALISES_STRUCT = ["body", "header", "nav", "main", "section", "article",
                  "aside", "footer", "div", "ul", "ol", "li", "form"]

ROLES_STRUCT = {
    "body": "Corps", "header": "En-tête", "nav": "Navigation",
    "main": "Corps principal", "section": "Section", "article": "Article",
    "aside": "Sidebar", "footer": "Pied de page", "div": "Bloc générique",
    "ul": "Liste UL", "ol": "Liste OL", "li": "Élément liste", "form": "Formulaire",
}


def extraire_structure(soup):
    """
    Extrait la structure de mise en page du <body> :
      zones sémantiques, blocs de navigation, disposition.
    Retourne : liste de dicts + liste de noeuds hiérarchiques
    """
    struct_list = []

    vus = set()
    for tag in BALISES_STRUCT:
        for el in soup.find_all(tag):
            id_el = el.get("id", "")
            classes = " ".join(el.get("class", []))
            role = el.get("role", "")
            ident = id_el or (classes.split()[0] if classes else "—")
            nb = len([c for c in el.children if hasattr(c, "name") and c.name])
            cle = (tag, id_el, classes)
            if cle in vus:
                continue
            vus.add(cle)
            struct_list.append({
                "Balise": f"<{tag}>",
                "Rôle": ROLES_STRUCT.get(tag, "—"),
                "ID/Classe": tronquer(ident, 22),
                "ARIA": role or "—",
                "Enfants": str(nb),
            })

    noeuds = []
    vus2 = set()

    def parcourir(el, depth=0, parent="racine"):
        nom = getattr(el, "name", None)
        if nom is None or nom not in BALISES_STRUCT:
            for e in getattr(el, "children", []):
                parcourir(e, depth, parent)
            return
        cle = (nom, depth, parent)
        if cle not in vus2:
            vus2.add(cle)
            noeuds.append({"tag": nom, "depth": depth, "parent_tag": parent, "index": len(noeuds)})
        for e in el.children:
            parcourir(e, depth + 1, nom)

    parcourir(soup.find("body") or soup)
    return struct_list, noeuds


def afficher_structure(struct_list):
    afficher_tableau(
        "STRUCTURE (<body> — zones & blocs)",
        ["Balise", "Rôle", "ID/Classe", "ARIA", "Enfants"], [10, 18, 24, 12, 7],
        [[s["Balise"], s["Rôle"], s["ID/Classe"], s["ARIA"], s["Enfants"]]
         for s in struct_list])


# ══════════════════════════════════════════════════════════════════════
# EXTRACTION 3 — CONTENU
# Balises : <h1>-<h6> <p> <a> <img> <figure> <figcaption>
#           <table> <thead> <tbody> <tr> <td> <th>
#           <blockquote> <pre> <code> <em> <strong> <span>
# ══════════════════════════════════════════════════════════════════════

BALISES_CONTENU = ["h1", "h2", "h3", "h4", "h5", "h6",
                   "p", "a", "img", "figure", "figcaption",
                   "table", "thead", "tbody", "tr", "td", "th",
                   "blockquote", "pre", "code", "em", "strong", "span"]


def extraire_contenu(soup, url_base=""):
    """
    Extrait les éléments de contenu :
      titres, paragraphes, liens, images, tableaux, citations.
    Retourne : liste de dicts + liste de noeuds hiérarchiques
    """
    contenu_list = []

    for tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        for el in soup.find_all(tag):
            txt = nettoyer(el.get_text(strip=True))
            if txt:
                contenu_list.append({"Type": tag.upper(), "Attribut": "—", "Valeur": tronquer(txt, 70)})

    for el in soup.find_all("p"):
        txt = nettoyer(el.get_text(strip=True))
        if txt:
            contenu_list.append({"Type": "p", "Attribut": "—", "Valeur": tronquer(txt, 70)})

    for el in soup.find_all("a", href=True):
        href = el["href"].strip()
        if href.startswith("javascript:") or href == "#":
            continue
        txt = nettoyer(el.get_text(strip=True)) or "(sans texte)"
        contenu_list.append({"Type": "a", "Attribut": tronquer(href, 30), "Valeur": tronquer(txt, 40)})

    for el in soup.find_all("img"):
        src = el.get("src", "—")
        alt = el.get("alt", "—")
        contenu_list.append({"Type": "img", "Attribut": tronquer(src, 30), "Valeur": tronquer(alt, 40)})

    for el in soup.find_all("table"):
        rows = len(el.find_all("tr"))
        contenu_list.append({"Type": "table", "Attribut": "rows", "Valeur": str(rows)})

    for el in soup.find_all("blockquote"):
        txt = nettoyer(el.get_text(strip=True))
        contenu_list.append({"Type": "blockquote", "Attribut": "—", "Valeur": tronquer(txt, 70)})

    noeuds = []
    vus = set()

    def parcourir(el, depth=0, parent="racine"):
        nom = getattr(el, "name", None)
        if nom is None or nom not in BALISES_CONTENU:
            for e in getattr(el, "children", []):
                parcourir(e, depth, parent)
            return
        cle = (nom, depth, parent)
        if cle not in vus:
            vus.add(cle)
            noeuds.append({"tag": nom, "depth": depth, "parent_tag": parent, "index": len(noeuds)})
        for e in el.children:
            parcourir(e, depth + 1, nom)

    parcourir(soup)
    return contenu_list, noeuds


def afficher_contenu(contenu_list):
    afficher_tableau(
        "CONTENU (titres · liens · images · tableaux)",
        ["Type", "Attribut", "Valeur"], [12, 32, 72],
        [[c["Type"], c["Attribut"], c["Valeur"]] for c in contenu_list])
