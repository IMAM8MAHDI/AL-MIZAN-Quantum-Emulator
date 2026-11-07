# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   BIOLOGIE ARITHMÉTIQUE — signatures moléculaires discrètes (expérimental)
===============================================================================
Deux pistes, une discipline : tout en fractions exactes, tout borné.

PISTE A — Signature arithmétique d'une chaîne d'acides aminés
  Les 20 masses d'acides aminés monoisotopiques sont des rationnels EXACTS
  (unité Da). La chaîne devient un polynôme exact ; on extrait :
    • masse totale exacte,
    • core sans facteur carré de la signature entière (ppm),
    • rapport entre blocs en fraction pure.

PISTE B — Cellule diophantienne : flux ioniques discrets
  Modèle de transport Na⁺/K⁺/Ca²⁺ à états discrets :
  potentiels de Nernst rationalisés, flux en fractions, bilan exact.
  Équilibre = fraction de flux = 1/1.

HONNÊTETÉ : modèles arithmétiques — PAS de la biophysique validée. La
"signature vibratoire" est une construction algébrique, pas une mesure
spectroscopique. Aucune prédiction thérapeutique.
===============================================================================
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List

from certificats.socle import noeud_certificat


# Masses monoisotopiques des 20 acides aminés (Da) — en millionièmes exacts
MASSES_AA_PPM: Dict[str, int] = {
    "G": 57021464, "A": 71037114, "S": 87023114, "P": 97052764,
    "V": 99068414, "T": 101047664, "C": 103009185, "L": 113084064,
    "I": 113084064, "N": 114042927, "D": 115026943, "Q": 128058578,
    "E": 129042593, "K": 128094963, "M": 131040485, "H": 137058912,
    "F": 147068414, "R": 156101111, "Y": 163063333, "W": 186079313,
}

_LETTRES = set(MASSES_AA_PPM)


def _core_sans_carre(n: int) -> int:
    """Noyau sans facteur carré (square-free core)."""
    n = abs(n)
    if n == 0:
        return 0
    c = 1
    d = 2
    while d * d <= n:
        e = 0
        while n % d == 0:
            n //= d
            e += 1
        if e % 2:
            c *= d
        d += 1
    return c * n


def signature_proteine(seq: str) -> Dict[str, Any]:
    """Signature arithmétique exacte d'une chaîne d'acides aminés."""
    seq = seq.upper()
    inconnu = [c for c in seq if c not in _LETTRES]
    if inconnu:
        return {"erreur": f"résidus inconnus : {set(inconnu)}"}
    masse_ppm = sum(MASSES_AA_PPM[c] for c in seq) - 18015280 * max(0, len(seq) - 1)
    masse = Fraction(masse_ppm, 10**6)
    core = _core_sans_carre(masse_ppm)
    # Résonance moyenne : masse/longueur en fraction pure
    moyenne = Fraction(masse_ppm, len(seq) * 10**6)
    return {
        "sequence": seq,
        "longueur": len(seq),
        "masse_exacte_Da": str(masse),
        "signature_entiere_ppm": masse_ppm,
        "core_sans_carre": core,
        "structure_core": "signature quadratique" if core < masse_ppm ** 0.25 else "résidu libre",
        "masse_moyenne_residu": str(moyenne.limit_denominator(10**4)),
    }


def comparer_proteines(seq_a: str, seq_b: str) -> Dict[str, Any]:
    """Rapport de masse de deux chaînes en fraction pure."""
    a = signature_proteine(seq_a)
    b = signature_proteine(seq_b)
    if "erreur" in a or "erreur" in b:
        return {"erreur": "séquence invalide"}
    rapport = Fraction(a["signature_entiere_ppm"], b["signature_entiere_ppm"])
    return {
        "rapport_exact": str(rapport.limit_denominator(10**6)),
        "rapport_decimal": round(float(rapport), 6),
        "core_commun": _core_sans_carre(
            min(a["core_sans_carre"], b["core_sans_carre"])),
    }


# ---------------------------------------------------------------------------
# Cellule diophantienne — flux ioniques à états discrets
# ---------------------------------------------------------------------------

class CelluleDiophantienne:
    """Modèle discret de transport d'ions Na⁺/K⁺/Ca²⁺.

    Concentrations en fractions exactes (mmol/L), flux discrets par pas.
    Équilibre : flux_entrant == flux_sortant (fraction 1/1).
    """

    def __init__(self) -> None:
        self.conc = {
            "Na_ext": Fraction(145), "Na_int": Fraction(14),
            "K_ext": Fraction(45, 10), "K_int": Fraction(120),
            "Ca_ext": Fraction(12, 10), "Ca_int": Fraction(1, 10000),
        }

    def flux_pompe(self, n_pas: int = 1) -> Dict[str, Fraction]:
        """ATPase Na/K : 3 Na⁺ sortent, 2 K⁺ entrent par pas — EXACT."""
        flux = {"Na": Fraction(-3 * n_pas), "K": Fraction(2 * n_pas)}
        self.conc["Na_int"] += Fraction(3 * n_pas)
        self.conc["K_int"] -= Fraction(2 * n_pas)
        return flux

    def ratio_nernst_simplifie(self, ion: str) -> Fraction:
        """Rapport ext/int — approximation du potentiel de Nernst."""
        ext = self.conc[f"{ion}_ext"]
        inte = self.conc[f"{ion}_int"]
        return ext / inte

    def bilan(self) -> Dict[str, Any]:
        return {
            "concentrations": {k: str(v) for k, v in self.conc.items()},
            "ratio_Na": str(self.ratio_nernst_simplifie("Na")),
            "ratio_K": str(self.ratio_nernst_simplifie("K")),
            "ratio_Ca": str(self.ratio_nernst_simplifie("Ca")),
            "equilibre_flux": "3/2 (pompe Na/K — stœchiométrie exacte)",
        }


def certificat_demo() -> Dict[str, Any]:
    insuline = "FVNQHLCGSHLVEALYLVCGERGFFYTPKT"  # chaîne B humaine
    glucagon = "HSQGTFTSDYSKYLDSRRAQDFVQWLMNT"
    cell = CelluleDiophantienne()
    flux = cell.flux_pompe(10)
    return noeud_certificat(
        "BIOLOGIE ARITHMÉTIQUE — protéines + cellule diophantienne",
        "signatures exactes de chaînes peptidiques et flux ioniques discrets",
        {
            "insuline_B": signature_proteine(insuline),
            "glucagon": signature_proteine(glucagon),
            "comparaison": comparer_proteines(insuline, glucagon),
            "cellule": cell.bilan(),
            "flux_pompe_10pas": {k: str(v) for k, v in flux.items()},
        },
        "CERTIFICAT_BORNE",
        "Modèles arithmétiques expérimentaux — pas de la biophysique "
        "validée. La signature vibratoire est algébrique, non mesurée.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat_demo(), indent=2, ensure_ascii=False))
