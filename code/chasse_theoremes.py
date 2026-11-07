# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   CHASSEUR DE THÉORÈMES — invariants algébriques cachés du système
===============================================================================
Un « théorème manquant » = une RELATION exacte entre constantes du
système, décidable par calcul exact (Fractions) et falsifiable.

Méthode : énumération des constantes déclarées (système + dérivées),
puis recherche exhaustive de :
  R1 — signatures carrées étendues (num OU dénominateur porte k²)
  R2 — relations linéaires petites : a·x + b·y = c·z, |coefs| ≤ 20
  R3 — relations multiplicatives : x·y = z, x/y carré ou k²·petit
  R4 — échelons entiers : x·n ∈ ℤ pour petit n (fractions → entiers)

Chaque relation trouvée = théorème candidat certifié par énumération.
===============================================================================
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any, Dict, List, Tuple

from certificats.socle import sceau

# ── Constantes déclarées du système (exactes, en Fraction) ──────────────────
CONSTANTES: Dict[str, Fraction] = {
    "MIZAN": Fraction(6225, 10000),          # 0.6225 = 249/400
    "LIGNE_REF": Fraction(122, 1000),        # 0.1220
    "EPSILON": Fraction(21, 1000),           # 0.0210
    "PLAFOND_EFFECTIF": Fraction(6015, 10000),
    "RMS": Fraction(24, 100),
    "M_SUBSTANCE": Fraction(24434),
    "POLE_MATIERE": Fraction(313),
    "Q_MECOIS": Fraction(2304),
    "Q_MEDINOIS": Fraction(1536),
    "AMPLITUDE": Fraction(9),
    "BASE_19": Fraction(19),
    "NIVEAUX": Fraction(4),
    "PPCM": Fraction(12),
    "DX": Fraction(6403563, 128),
    "DY": Fraction(93987, 2),
    "DZ": Fraction(135000000),
    "DT": Fraction(17292418731, 128),
    "C_SUBSTANCE": Fraction(313),
}


def _facteur_carre(n: int) -> int:
    n = abs(n)
    if n == 0:
        return 0
    k = math.isqrt(n)
    while k > 1:
        if n % (k * k) == 0:
            return k
        k -= 1
    return 1


def chasser() -> Dict[str, Any]:
    trouves: List[Dict[str, Any]] = []

    # ── R1 : signature carrée sur num OU dénominateur ───────────────────────
    sign = {}
    for nom, v in CONSTANTES.items():
        kn, kd = _facteur_carre(v.numerator), _facteur_carre(v.denominator)
        if kn > 1 or kd > 1:
            sign[nom] = f"num {v.numerator}={kn}²·{v.numerator // (kn*kn) if kn>1 else v.numerator} " \
                        f"den {v.denominator}={kd}²·{v.denominator // (kd*kd) if kd>1 else v.denominator}"
    trouves.append({
        "regle": "R1 signature carrée",
        "constantes_avec_signature": sign,
        "nb": len(sign),
    })

    # ── R2 : relations linéaires a·x + b·y = c·z ────────────────────────────
    noms = list(CONSTANTES)
    index = {CONSTANTES[z]: z for z in noms}
    relations = []
    for i, x in enumerate(noms):
        for j, y in enumerate(noms):
            if j <= i:
                continue
            vx, vy = CONSTANTES[x], CONSTANTES[y]
            for a in range(-10, 11):
                for b in range(-10, 11):
                    if a == 0 and b == 0:
                        continue
                    w = a * vx + b * vy
                    if w in index and index[w] not in (x, y):
                        relations.append(f"{a}·{x} + {b}·{y} = {index[w]}")
    trouves.append({"regle": "R2 relations linéaires a·x+b·y=z, |a,b|≤10",
                    "relations": relations[:60], "nb": len(relations)})

    # ── R3 : produits/quotients → carré ou constante du système ─────────────
    prod = []
    for i, x in enumerate(noms):
        for j, y in enumerate(noms):
            if j <= i:
                continue
            p = CONSTANTES[x] * CONSTANTES[y]
            big = p.numerator * p.denominator
            if big < 10**12:
                kp = _facteur_carre(big)
                if kp > 1 and big == kp * kp:
                    prod.append(f"{x}·{y} = {p} = {kp}²")
            for z in noms:
                if CONSTANTES[x] * CONSTANTES[y] == CONSTANTES[z]:
                    prod.append(f"{x}·{y} = {z}")
    trouves.append({"regle": "R3 produits exacts/carrés",
                    "relations": prod[:40], "nb": len(prod)})

    # ── R4 : échelons entiers ────────────────────────────────────────────────
    entiers = {}
    for nom, v in CONSTANTES.items():
        for n in (2, 4, 8, 16, 32, 64, 128):
            w = v * n
            if w.denominator == 1:
                entiers.setdefault(nom, []).append(f"{nom}·{n} = {w.numerator}")
                break
    trouves.append({"regle": "R4 échelons entiers", "details": entiers,
                    "nb": len(entiers)})

    return {
        "chasse": "THÉORÈMES CACHÉS — relations exactes entre constantes",
        "nb_constantes": len(CONSTANTES),
        "familles": trouves,
        "timestamp": "scellé",
    }


def afficher(r: Dict[str, Any]) -> str:
    lignes = ["", "═" * 66, "  CHASSEUR DE THÉORÈMES — invariants cachés", "═" * 66]
    for f in r["familles"]:
        lignes.append(f"\n  ◆ {f['regle']}  ({f['nb']} trouvailles)")
        for cle, val in f.items():
            if cle in ("regle", "nb"):
                continue
            if isinstance(val, dict):
                for k2, v2 in list(val.items())[:15]:
                    lignes.append(f"      {k2} : {v2}")
            elif isinstance(val, list):
                for v2 in val[:15]:
                    lignes.append(f"      {v2}")
            else:
                lignes.append(f"      {cle} : {val}")
    return "\n".join(lignes)


if __name__ == "__main__":
    r = chasser()
    r["sceau_sha256"] = sceau(r)
    print(afficher(r))
    print("\nsceau :", r["sceau_sha256"][:40])
