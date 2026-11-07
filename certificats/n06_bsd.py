# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Nœud 6 — BIRCH & SWINNERTON-DYER.

Énoncé : pour une courbe elliptique E/Q, le rang de E(Q) égale l'ordre
d'annulation de L(E,s) en s=1, et le terme dominant encode Ш, Rég, Tors.

Certificats finis réels :
  a) borne de Hasse |a_p| ≤ 2√p — THÉORÈME vérifié exhaustivement par
     comptage de points #E(F_p) pour p ≤ P sur courbes nommées ;
  b) sommes partielles de L(E,1) = Σ a_n/n (a_n multiplicatif, récurrence
     a_{p²}=a_p²−p) — indication numérique de l'ordre d'annulation.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from .socle import noeud_certificat


def _premiers(borne: int) -> List[int]:
    crible = [True] * (borne + 1)
    crible[0:2] = [False, False]
    for i in range(2, int(borne ** 0.5) + 1):
        if crible[i]:
            crible[i * i::i] = [False] * len(crible[i * i::i])
    return [i for i, v in enumerate(crible) if v]


def _points_mod_p(a: int, b: int, p: int) -> int:
    """#E(F_p) pour E : y² = x³ + ax + b (forme courte, p > 3)."""
    residus = {pow(x, 2, p) for x in range(p)}
    n = 1  # point à l'infini
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            n += 1
        elif rhs in residus:
            n += 2
    return n


def _a_n(ap: Dict[int, int], n: int) -> int:
    """Coefficient de Dirichlet a_n multiplicatif (récurrence de Hecke)."""
    if n == 1:
        return 1
    # factorisation n = p^k · m
    for p in sorted(ap):
        if n % p == 0:
            k, m = 0, n
            while m % p == 0:
                m //= p
                k += 1
            a_pk = ap.get(p, 0)
            if k == 1:
                apk = a_pk
            else:
                # a_{p^k} = a_p · a_{p^{k-1}} − p · a_{p^{k-2}}
                v0, v1 = 1, a_pk
                for _ in range(2, k + 1):
                    v0, v1 = v1, a_pk * v1 - p * v0
                apk = v1
            return apk * _a_n(ap, m)
    return 1


def _certificat_courbe(nom: str, a: int, b: int, borne_p: int = 97) -> Dict[str, Any]:
    premiers = [p for p in _premiers(borne_p) if p > 3]
    ap: Dict[int, int] = {}
    violations_hasse = []
    for p in premiers:
        nb = _points_mod_p(a, b, p)
        ap[p] = p + 1 - nb
        if abs(ap[p]) > 2 * math.sqrt(p):
            violations_hasse.append({"p": p, "a_p": ap[p]})
    # Somme partielle L(E,1) ≈ Σ_{n≤N} a_n/n — convergence lente : INDICATION
    n_max = 3000
    somme = sum(_a_n(ap, n) / n for n in range(1, n_max + 1))
    return {
        "courbe": nom,
        "equation": f"y² = x³ {'+' if a >= 0 else '−'} {abs(a)}x "
                    f"{'+' if b >= 0 else '−'} {abs(b)}",
        "premiers_testes": len(premiers),
        "borne_p": borne_p,
        "hasse_|a_p|≤2√p_violations": violations_hasse,
        "hasse_respectee_partout": not violations_hasse,
        "L(E,1)_somme_partielle": round(somme, 6),
        "indication_rang": ("L(E,1) ≈ 0 → rang ≥ 1 probable"
                            if abs(somme) < 0.05 else "L(E,1) ≠ 0 → rang 0 probable"),
    }


def certificat() -> Dict[str, Any]:
    courbes = {
        "E1_32a": _certificat_courbe("y²=x³−x", -1, 0),
        "E2_11a": _certificat_courbe("y²=x³−4x+4", -4, 4),
        "E3_37a": _certificat_courbe("y²=x³−16x+16", -16, 16),
    }
    hasse_globale = all(c["hasse_respectee_partout"] for c in courbes.values())
    return noeud_certificat(
        "BIRCH & SWINNERTON-DYER",
        "rang E(Q) = ord_{s=1} L(E,s), et formule du terme dominant ?",
        {
            "courbes": courbes,
            "hasse_verifie_exhaustion": hasse_globale,
        },
        "CERTIFICAT_BORNE",
        "Hasse (théorème) vérifié par comptage exact sur tous les p ≤ 97 ; "
        "L(E,1) partielle = indication numérique. Le problème porte sur "
        "TOUTES les courbes — domaine infini.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat(), indent=2, ensure_ascii=False))
