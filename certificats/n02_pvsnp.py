# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Nœud 2 — P vs NP.

Énoncé : existe-t-il un algorithme polynomial décidant SAT pour toute
instance ? Aucune expérience finie ne peut trancher — certificat de
MESURE : croissance empirique du solveur exhaustif 3-SAT vs référence
polynomiale (tri). Prolifération honnête : le fruit est une courbe, pas
une preuve.
"""

from __future__ import annotations

import itertools
import math
import time
from typing import Any, Dict

from .socle import noeud_certificat


def _sat_exhaustif(clauses, n: int) -> bool:
    """Résout SAT par force brute sur 2^n affectations."""
    for bits in itertools.product((False, True), repeat=n):
        ok = True
        for clause in clauses:
            sat = any((bits[abs(l) - 1] if l > 0 else not bits[-l - 1])
                      for l in clause)
            if not sat:
                ok = False
                break
        if ok:
            return True
    return False


def _instance_3sat(n: int):
    """Instance déterministe (graine fixe) : clauses pseudo-aléatoires."""
    clauses = []
    rng = 0xC0FFEE + n
    for _ in range(4 * n):
        clause = []
        for _ in range(3):
            rng = (1103515245 * rng + 12345) % (2 ** 31)
            lit = (rng % n) + 1
            if rng & 1:
                lit = -lit
            clause.append(lit)
        clauses.append(clause)
    return clauses


def _mesure_croissance() -> Dict[str, Any]:
    """Temps du solveur exhaustif n=4..16 + référence tri O(n log n)."""
    mesures = []
    for n in (4, 6, 8, 10, 12, 14):
        t0 = time.perf_counter()
        _sat_exhaustif(_instance_3sat(n), n)
        dt = time.perf_counter() - t0
        mesures.append({"n": n, "temps_s": round(dt, 6)})

    t0 = time.perf_counter()
    sorted(range(10_000_0, 0, -1))
    temps_tri = time.perf_counter() - t0

    ratios = [round(mesures[i + 1]["temps_s"] / max(mesures[i]["temps_s"], 1e-9), 2)
              for i in range(len(mesures) - 1)]
    return {
        "mesures_3sat_exhaustif": mesures,
        "ratios_croissance_n_plus_2": ratios,
        "reference_tri_1e5_elements_s": round(temps_tri, 6),
        "interpretation": "croissance ~exponentielle mesurée (ratios >> 1) "
                          "vs tri quasi-linéaire — observation, pas preuve",
    }


def certificat() -> Dict[str, Any]:
    return noeud_certificat(
        "P vs NP",
        "∃A polynomial : ∀φ, A(φ)=SAT(φ) ?  (P = NP ?)",
        _mesure_croissance(),
        "MESURE_INDICATION",
        "L'écart de croissance est observable ; décider P vs NP exige une "
        "preuve sur TOUS les algorithmes possibles — domaine infini.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat(), indent=2, ensure_ascii=False))
