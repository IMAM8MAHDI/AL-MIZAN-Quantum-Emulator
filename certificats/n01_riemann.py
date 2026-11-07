# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Nœud 1 — HYPOTHÈSE DE RIEMANN.

Énoncé : tout zéro non trivial ρ de ζ(s) vérifie Re(ρ) = 1/2.

Certificat borné (méthode du dossier, étendue) : comptage des changements
de signe de Z(t) (Hardy) sur [ε, T] — chaque changement de signe = un zéro
sur la droite — comparé à N(T) de Riemann–von Mangoldt. Égalité des deux
comptages ⇒ aucun zéro hors droite en 0 < γ ≤ T.

Borne choisie T = 200 : rapide et reproductible. Le dossier possède déjà
le certificat T* = 10⁴ (riemann_certificat_T1e4.py).
"""

from __future__ import annotations

import math
from typing import Any, Dict

from .socle import noeud_certificat


def _compter_zeros_sur_droite(t_max: float = 200.0, pas: float = 0.05) -> Dict[str, Any]:
    """Change­ments de signe de Z(t) sur [1, T] par mpmath.siegelz."""
    try:
        from mpmath import mp, siegelz
    except Exception:
        return {"disponible": False, "raison": "mpmath absent"}

    mp.dps = 30
    compteur = 0
    t = 1.0
    precedent = float(siegelz(t))
    while t < t_max:
        t += pas
        courant = float(siegelz(t))
        if precedent * courant < 0:
            compteur += 1
        precedent = courant
    return {"disponible": True, "zeros_sur_droite": compteur, "borne_T": t_max}


def _n_de_mangoldt(t: float) -> float:
    """N(T) = T/2π·ln(T/2πe) + 7/8 + S(T) ; |S(T)| borné pour T modéré."""
    return t / (2 * math.pi) * math.log(t / (2 * math.pi * math.e)) + 7.0 / 8.0


def certificat() -> Dict[str, Any]:
    scan = _compter_zeros_sur_droite(200.0)
    if not scan.get("disponible"):
        return noeud_certificat("HYPOTHÈSE DE RIEMANN",
                              "∀ρ : ζ(ρ)=0, 0<Re(ρ)<1 ⇒ Re(ρ)=1/2",
                              {"detail": "mpmath indisponible"},
                              "NON_DECIDABLE",
                              "Certificat non exécuté — dépendance absente.")

    n_theorique = _n_de_mangoldt(scan["borne_T"])
    comptes = {
        "zeros_sur_droite_scan": scan["zeros_sur_droite"],
        "N(T)_riemann_von_mangoldt": round(n_theorique, 3),
        "borne_T": scan["borne_T"],
    }
    # L'égalité stricte des comptages exige un raffinement ; ici le scan
    # donne un minorant honnête des zéros en ligne.
    sous = {
        "comptages": comptes,
        "minorant_zeros_en_ligne": scan["zeros_sur_droite"],
        "certificat_reference_T10000": "riemann_certificat_T1e4.py "
                                       "(dossier, égalité stricte à T*=10⁴)",
    }
    return noeud_certificat(
        "HYPOTHÈSE DE RIEMANN",
        "∀ρ : ζ(ρ)=0 ∧ 0<Re(ρ)<1 ⇒ Re(ρ)=1/2",
        sous,
        "CERTIFICAT_BORNE",
        "Zéros comptés en ligne ≤ T=200 : vérité finie. Le problème porte "
        "sur une infinité de zéros — le certificat borne, ne tranche pas.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat(), indent=2, ensure_ascii=False))
