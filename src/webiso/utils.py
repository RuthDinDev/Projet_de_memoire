"""Utilitaires partagés d'affichage (texte et tableaux ASCII)."""


def tronquer(t, n):
    """Raccourcit un texte trop long pour l'affichage."""
    if not t:
        return "—"
    t = t.strip()
    return t if len(t) <= n else t[: n - 3] + "..."


def nettoyer(t):
    """Uniformise les espaces dans un texte."""
    if not t:
        return ""
    return " ".join(t.split())


def afficher_tableau(titre, cols, widths, lignes):
    """Affiche un tableau ASCII dans le terminal, comme un mini-rapport visuel."""
    SEP = " │ "
    total = sum(widths) + len(widths) * len(SEP) + 4

    def sep(g="├", m="┼", d="┤", r="─"):
        return g + m.join(r * (w + 2) for w in widths) + d

    def ligne(cells):
        return "│ " + SEP.join(str(v).ljust(w) for v, w in zip(cells, widths)) + " │"

    print()
    print("─" * total)
    print(f"  {titre}")
    print("─" * total)
    if not lignes:
        print("  (aucun)\n")
        return
    print(sep("╭", "┬", "╮"))
    print(ligne(cols))
    print(sep("├", "┼", "┤"))
    for i, l in enumerate(lignes):
        print(ligne(l))
        if i < len(lignes) - 1:
            print(sep())
    print(sep("╰", "┴", "╯"))
    print(f"  → {len(lignes)} élément(s)\n")
