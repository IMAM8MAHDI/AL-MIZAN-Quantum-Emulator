# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""Nœud 4 — YANG-MILLS : existence & trou de masse.

Énoncé : construire une théorie de Yang-Mills quantique 4D non abélienne
rigoureuse et prouver l'existence d'un gap de masse Δ > 0.

Certificat borné (analogie honnête) : le gap de masse est un gap SPECTRAL
du hamiltonien. On calcule exactement le gap d'un modèle de jauge jouet —
la chaîne d'Ising transverse H = −Σ σzσz − gΣ σx — par diagonalisation
exacte (n sites, 2^n matrice). Δ = E₁ − E₀ > 0 loin du point critique.
"""

from __future__ import annotations

import math
from typing import Any, Dict

from .socle import noeud_certificat


def _gap_ising_transverse(n_sites: int = 9, g: float = 1.5) -> Dict[str, Any]:
    """Diagonalisation exacte de la chaîne d'Ising transverse."""
    try:
        import numpy as np
    except Exception:
        return {"disponible": False, "raison": "numpy absent"}

    dim = 1 << n_sites
    h = np.zeros((dim, dim))
    for i in range(dim):
        # terme -g Σ σx : flip un bit, amplitude -g
        for q in range(n_sites):
            h[i, i ^ (1 << q)] -= g
        # terme -Σ σz σz : diagonale
        for q in range(n_sites):
            b1 = (i >> q) & 1
            b2 = (i >> ((q + 1) % n_sites)) & 1
            h[i, i] -= 1.0 if b1 == b2 else -1.0
    valeurs = np.linalg.eigvalsh(h)
    valeurs.sort()
    e0, e1 = float(valeurs[0]), float(valeurs[1])
    return {
        "disponible": True,
        "modele": "chaîne d'Ising transverse (analogie gap de masse)",
        "n_sites": n_sites, "g": g,
        "E0": round(e0, 6), "E1": round(e1, 6),
        "gap_spectral": round(e1 - e0, 6),
        "gap_positif": bool(e1 - e0 > 1e-9),
    }


def certificat() -> Dict[str, Any]:
    r = _gap_ising_transverse()
    statut = "CERTIFICAT_BORNE" if r.get("disponible") else "NON_DECIDABLE"
    return noeud_certificat(
        "YANG-MILLS (existence & trou de masse)",
        "∃ théorie YM 4D rigoureuse avec gap de masse Δ > 0 ?",
        r,
        statut,
        "Gap > 0 mesuré dans un modèle jouet 1D exact — analogie honnête "
        "au mass gap, pas la théorie de jauge 4D non abélienne.")


if __name__ == "__main__":
    import json
    print(json.dumps(certificat(), indent=2, ensure_ascii=False))
