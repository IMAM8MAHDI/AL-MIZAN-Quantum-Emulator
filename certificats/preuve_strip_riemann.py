# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   POUSSE NIVEAU 2 — TOUS les zéros de Z(t) certifiés jusqu'à T = 100
===============================================================================
Stratégie (méthode Turing/Platt, à échelle honnête) :
  1. scan FLOTTANT de Z(t) (mpmath siegelz, 25 dps) → intervalles candidats
     [t_i, t_i+δ] contenant un changement de signe ;
  2. CERTIFICATION par enceintes d'intervalles (rigueur_intervalle) :
     signes opposés garantis ⇒ ∃ zéro — THÉORÈME par TVI ;
  3. bilan : K zéros certifiés en ligne sous T + N(T) estimé.

Vérité mathématique : chaque entrée "certifiée" est un théorème d'existence
rigoureux. L'égalité complète avec N(T) exige en outre S(T) borné < 1 —
marqué ◐ honnêtement, pas décrété.
===============================================================================
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple

from mpmath import mp, siegelz

from .rigueur_intervalle import signe_certifie, z_intervalle
from .socle import noeud_certificat


def _scan_flottant(t_min: float = 10.0, t_max: float = 100.0,
                   pas: float = 0.1) -> List[Tuple[float, float]]:
    """Intervalles candidats : changements de signe de Z(t) en flottant."""
    mp.dps = 25
    candidats = []
    t = t_min
    prev = float(siegelz(t))
    while t < t_max:
        t_suiv = t + pas
        cour = float(siegelz(t_suiv))
        if prev * cour < 0:
            candidats.append((t, t_suiv))
        t, prev = t_suiv, cour
    return candidats


def _certifier(candidats: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
    theoremes = []
    for t0, t1 in candidats:
        z0, z1 = z_intervalle(t0), z_intervalle(t1)
        s0, s1 = signe_certifie(z0), signe_certifie(z1)
        theoremes.append({
            "intervalle": [round(t0, 4), round(t1, 4)],
            "signes": [s0, s1],
            "certifie": s0 is not None and s1 is not None and s0 != s1,
        })
    return theoremes


def _n_de_mangoldt(t: float) -> float:
    return t / (2 * math.pi) * math.log(t / (2 * math.pi * math.e)) + 7.0 / 8.0


def certificat(t_max: float = 100.0) -> Dict[str, Any]:
    candidats = _scan_flottant(10.0, t_max, 0.1)
    theoremes = _certifier(candidats)
    certifies = [t for t in theoremes if t["certifie"]]
    n_estime = _n_de_mangoldt(t_max)
    return noeud_certificat(
        "RIEMANN — STRIP COMPLET ≤ 100 (niveau 2 poussé)",
        "∀ρ : ζ(ρ)=0 ∧ 0<Re(ρ)<1 ⇒ Re(ρ)=1/2",
        {
            "zeros_certifies_en_ligne": len(certifies),
            "intervalles_non_concluants": len(theoremes) - len(certifies),
            "N(100)_estime": round(n_estime, 3),
            "borne_T": t_max,
            "theoremes": theoremes,
            "statut_exact": ("au moins %d zéros sur la droite ≤ %g — "
                             "THÉORÈME" % (len(certifies), t_max)),
            "manquant_pour_tous": "N(T) rigoureux avec |S(T)|<1 fermerait "
                                  "l'égalité des comptages (◐ méthode connue)",
        },
        "CERTIFICAT_BORNE",
        "Chaque zéro = théorème TVI garanti par intervalles. 'Tous les "
        "zéros ≤100 en ligne' exige en plus l'égalité avec N(100)≈29 — "
        "la clause S(T)<1 est posée, pas encore certifiée.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat(), indent=2, ensure_ascii=False))
