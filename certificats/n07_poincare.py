# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Nœud 7 — CONJECTURE DE POINCARÉ (résolue, Perelman 2003).

Énoncé : toute 3-variété close simplement connexe est homéomorphe à S³.

Fruit borné : certificat COMBINATOIRE sur une triangulation de la sphère
(octaèdre) — caractéristique d'Euler χ = V − E + F = 2 et premier groupe
d'homologie b₁ = 0, calculés EXACTEMENT par algèbre linéaire sur GF(2).
Rappel : la conjecture est un THÉORÈME depuis Perelman (médaille 2006).
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .socle import noeud_certificat


def _rang_gf2(matrice: List[List[int]]) -> int:
    """Rang d'une matrice binaire par élimination de Gauss sur GF(2)."""
    m = [ligne[:] for ligne in matrice if any(ligne)]
    if not m:
        return 0
    lignes, cols = len(m), len(m[0])
    rang = 0
    for c in range(cols):
        pivot = next((r for r in range(rang, lignes) if m[r][c] == 1), None)
        if pivot is None:
            continue
        m[rang], m[pivot] = m[pivot], m[rang]
        for r in range(lignes):
            if r != rang and m[r][c] == 1:
                m[r] = [x ^ y for x, y in zip(m[r], m[rang])]
        rang += 1
        if rang == lignes:
            break
    return rang


def _octaedre() -> Tuple[List[List[int]], List[List[int]], int, int, int]:
    """Octaèdre : 6 sommets (3 paires opposées), 12 arêtes, 8 faces.

    Arête = toute paire sauf les 3 paires de sommets opposés ;
    face = un sommet de chaque paire opposée (2³ = 8 triangles).
    """
    sommets = list(range(6))
    opposes = {(0, 5), (1, 4), (2, 3)}
    aretes = [(i, j) for i in sommets for j in sommets
              if i < j and (i, j) not in opposes]
    faces = [(a, b, c) for a in (0, 5) for b in (1, 4) for c in (2, 3)]

    idx_e = {e: i for i, e in enumerate(aretes)}
    # ∂1 : arêtes → sommets
    d1 = [[0] * len(sommets) for _ in aretes]
    for (a, b), i in idx_e.items():
        d1[i][a] = d1[i][b] = 1
    # ∂2 : faces → arêtes
    d2 = [[0] * len(aretes) for _ in faces]
    for fi, (a, b, c) in enumerate(faces):
        for e in ((a, b), (b, c), (a, c)):
            ee = e if e in idx_e else (e[1], e[0])
            d2[fi][idx_e[ee]] = 1
    return d1, d2, len(sommets), len(aretes), len(faces)


def certificat() -> Dict[str, Any]:
    d1, d2, v, e, f = _octaedre()
    rang_d1 = _rang_gf2(d1)
    rang_d2 = _rang_gf2(d2)
    b0 = v - rang_d1
    b1 = (e - rang_d1) - rang_d2
    chi = v - e + f
    return noeud_certificat(
        "CONJECTURE DE POINCARÉ",
        "∀M³ close simplement connexe : M ≃ S³ ?",
        {
            "triangulation": "octaèdre (sphère S² — vérification de méthode)",
            "V": v, "E": e, "F": f,
            "chi_euler": chi,
            "b0_connexe": b0,
            "b1_homologie": b1,
            "simplement_connexe_homologique": bool(chi == 2 and b1 == 0),
            "theoreme_reference": "Perelman 2003 — conjecture DÉMONTRÉE",
        },
        "DEJA_DEMONTRE",
        "χ=2 et b₁=0 vérifiés par GF(2) exact — méthode combinatoire "
        "illustrée sur S². Poincaré est un théorème, pas une conjecture.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat(), indent=2, ensure_ascii=False))
