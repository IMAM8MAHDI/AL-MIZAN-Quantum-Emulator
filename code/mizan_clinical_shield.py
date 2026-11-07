# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   MIZAN CLINICAL SHIELD — armement arithmétique du clinicien (expérimental)
===============================================================================
Deux outils pour le praticien, bâtis sur l'infrastructure de certificats :

  1. FENÊTRE CHRONOTHÉRAPEUTIQUE : à partir de la phase circadienne mesurée
     du patient, calcule la fenêtre horaire où l'administration maximise la
     résonance avec l'oscillateur biologique (chronothérapie).
  2. SCORE AL-MIZAN (SAM) : index 0–100 de stabilité harmonique d'un signal
     de variabilité (ex. VFC). Une chute brutale du score = rupture de la
     structure → alerte précoce, avant les symptômes visibles.

HONNÊTETÉ MÉDICALE : outil de recherche, pas un dispositif médical.
Aucune décision clinique ne doit s'appuyer sur ce module sans validation
réglementaire. Il calcule des indicateurs, il ne prescrit pas.
===============================================================================
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import Any, Dict, List, Optional

from certificats.socle import noeud_certificat
from sante_chronobiologie import analyser_rythme, periode_dominante


# ---------------------------------------------------------------------------
# 1. FENÊTRE CHRONOTHÉRAPEUTIQUE
# ---------------------------------------------------------------------------

def fenetre_chronotherapeutique(phase_mesuree_h: float,
                                phase_cible_h: float = 2.0,
                                tolerance_h: float = 0.75) -> Dict[str, Any]:
    """Fenêtre d'administration optimale.

    phase_mesuree_h : heure de pic biologique mesurée (ex. pic cortisol)
    phase_cible_h   : phase optimale de la cible thérapeutique
    Retourne l'intervalle [début, fin] où le déphasage est minimal.
    """
    decalage = (phase_cible_h - phase_mesuree_h) % 24
    centre = (phase_mesuree_h + decalage) % 24
    debut = (centre - tolerance_h) % 24
    fin = (centre + tolerance_h) % 24
    rapport = Fraction(phase_mesuree_h / 24).limit_denominator(48)
    return {
        "phase_patient_h": phase_mesuree_h,
        "phase_cible_h": phase_cible_h,
        "decalage_h": round(decalage, 2),
        "fenetre_optimale": [round(debut, 2), round(fin, 2)],
        "fraction_synchronie": str(rapport),
        "note": "la fenêtre suit le pic de réceptivité de l'oscillateur",
    }


# ---------------------------------------------------------------------------
# 2. SCORE AL-MIZAN (SAM) — stabilité harmonique 0-100
# ---------------------------------------------------------------------------

def score_almizan(signal: List[float], dt: float = 1.0) -> Dict[str, Any]:
    """SAM = 100·(stabilité de la fraction dominante + force de corrélation)/2.

    Un signal hautement périodique (fraction pure, corrélation forte)
    donne un score proche de 100 ; le chaos donne ~0.
    """
    p = periode_dominante(signal, dt)
    force = max(0.0, min(1.0, p["force_correlation"]))
    rapport = Fraction(p["periode_heures"] / 24).limit_denominator(48)
    residu = abs(float(rapport) * 24 - p["periode_heures"]) / 24
    purete = max(0.0, 1.0 - residu)
    sam = round(100 * (0.5 * force + 0.5 * purete), 1)
    return {
        "SAM": sam,
        "force_correlation": round(force, 3),
        "purete_fraction": round(purete, 3),
        "fraction": str(rapport),
        "alerte": "CRITIQUE" if sam < 40 else "VIGILANCE" if sam < 70 else "STABLE",
    }


def serie_sam(fenetres: List[List[float]], dt: float = 1.0) -> Dict[str, Any]:
    """Score sur des fenêtres successives — détecte la CHUTE brutale."""
    scores = [score_almizan(w, dt)["SAM"] for w in fenetres]
    chutes = [round(scores[i - 1] - scores[i], 1)
              for i in range(1, len(scores))]
    max_chute = max(chutes) if chutes else 0.0
    return {
        "scores_par_fenetre": scores,
        "chute_maximale": max_chute,
        "alerte_precoce": max_chute >= 30,
        "note": "une chute ≥ 30 pts annonce la rupture harmonique",
    }


# ---------------------------------------------------------------------------
# Certificat de démonstration
# ---------------------------------------------------------------------------

def certificat_demo() -> Dict[str, Any]:
    random.seed(42)
    # VFC stable (3 fenêtres) puis rupture (chaos)
    sain = [[math.sin(2 * math.pi * t / 24) + 0.05 * random.gauss(0, 1)
             for t in range(96)] for _ in range(3)]
    rupture = [[random.gauss(0, 1) for _ in range(96)] for _ in range(2)]
    return noeud_certificat(
        "MIZAN CLINICAL SHIELD — démonstration (signaux synthétiques)",
        "fenêtre chronothérapeutique + score SAM d'alerte précoce",
        {
            "fenetre_exemple": fenetre_chronotherapeutique(21.5, 2.0),
            "sam_serie": serie_sam(sain + rupture),
        },
        "CERTIFICAT_BORNE",
        "Outil de recherche — PAS un dispositif médical. Aucune "
        "décision clinique sans validation réglementaire.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat_demo(), indent=2, ensure_ascii=False))
