# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   SANTÉ — CHRONOBIOLOGIE : analyse de rythmes biologiques (module expérimental)
===============================================================================
Application de la méthode AL-MIZAN aux rythmes du vivant :

  • Détection de périodes dominantes dans un signal biologique
    (mélatonine, cortisol, variabilité cardiaque) par autocorrélation —
    méthode mathématique standard, pas de mysticisme.
  • Approximation rationnelle : les rapports de périodes mesurés sont
    approchés par fractions continues (convergents) — le seul sens
    rigoureux où une « fraction pure » apparaît dans du vivant.
  • Certificat borné : chaque résultat porte tolérance et bornes.

HONNÊTETÉ : ce module N'EST PAS un outil médical. Les signaux biologiques
sont bruités ; une fraction approchée est une description, pas un
diagnostic. Toute application clinique exige validation médicale.
===============================================================================
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Any, Dict, List, Optional

from certificats.socle import noeud_certificat


def _autocorrelation(signal: List[float], lag_max: int) -> List[float]:
    """Autocorrélation normalisée pour lags 1..lag_max."""
    n = len(signal)
    moy = sum(signal) / n
    var = sum((x - moy) ** 2 for x in signal) or 1.0
    return [sum((signal[t] - moy) * (signal[t + k] - moy)
                for t in range(n - k)) / var
            for k in range(1, lag_max + 1)]


def periode_dominante(signal: List[float], dt: float = 1.0,
                      lag_max: Optional[int] = None) -> Dict[str, Any]:
    """Période dominante par premier pic fort de l'autocorrélation."""
    n = len(signal)
    lag_max = lag_max or n // 2
    ac = _autocorrelation(signal, lag_max)
    meilleur_k, meilleur_v = 0, -1.0
    for k in range(1, lag_max - 1):
        if ac[k - 1] < ac[k] > ac[k + 1] and ac[k] > meilleur_v:
            meilleur_k, meilleur_v = k + 1, ac[k]
    return {"periode_heures": meilleur_k * dt,
            "force_correlation": round(meilleur_v, 4),
            "confiance": "forte" if meilleur_v > 0.5 else
                         "modérée" if meilleur_v > 0.2 else "faible"}


def fraction_rationnelle(x: float, denom_max: int = 100) -> Fraction:
    """Meilleure approximation rationnelle (fractions continues)."""
    return Fraction(x).limit_denominator(denom_max)


def analyser_rythme(signal: List[float], nom: str,
                    dt_heures: float = 1.0) -> Dict[str, Any]:
    """Pipeline complet : période → rapport au jour en fraction pure."""
    p = periode_dominante(signal, dt_heures)
    jour = Fraction(24)
    rapport = fraction_rationnelle(p["periode_heures"] / 24, 48)
    ecart = abs(float(rapport) * 24 - p["periode_heures"])
    return {
        "signal": nom,
        "periode_detectee_h": p["periode_heures"],
        "confiance": p["confiance"],
        "rapport_au_jour": f"{rapport.numerator}/{rapport.denominator}",
        "fraction_pure": str(rapport),
        "ecart_h": round(ecart, 4),
    }


def certificat_demo() -> Dict[str, Any]:
    """Démonstration : mélatonine synthétique à 24h + rythme perturbé."""
    import random
    random.seed(7)
    sain = [0.5 + 0.5 * math.sin(2 * math.pi * t / 24)
            + 0.05 * random.gauss(0, 1) for t in range(240)]
    perturbe = [0.5 + 0.5 * math.sin(2 * math.pi * t / 25.3)
                + 0.15 * random.gauss(0, 1) for t in range(240)]
    return noeud_certificat(
        "CHRONOBIOLOGIE — rythme circadien (module expérimental)",
        "détecter la période dominante et sa fraction pure rapportée au jour",
        {
            "rythme_sain": analyser_rythme(sain, "mélatonine 24h"),
            "rythme_perturbe": analyser_rythme(perturbe, "désync. 25.3h"),
            "methode": "autocorrélation + convergents de fractions continues",
        },
        "CERTIFICAT_BORNE",
        "Signaux synthétiques — pas un outil médical. Le passage à des "
        "données cliniques réelles exige éthique + validation.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat_demo(), indent=2, ensure_ascii=False))
