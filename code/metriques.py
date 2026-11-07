# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   MÉTRIQUES QUANTIQUES — TRACE PARTIELLE, BLOCH, CONCURRENCE
===============================================================================
Extraction de grandeurs physiques depuis un vecteur d'état pur :

  • trace partielle      → matrice densité réduite d'un qubit
  • vecteur de Bloch     → (x, y, z) de chaque qubit
  • concurrence          → intrication C ∈ [0 ; 1] d'une paire de qubits
                           (formule exacte pour état pur à 2 qubits)

Les calculs sont exacts — aucune approximation Monte Carlo.
===============================================================================
"""

from __future__ import annotations

import math
from typing import Dict, Sequence, Tuple


def matrice_reduite(etat: Sequence[complex], nb_qubits: int,
                    qubit: int) -> Tuple[complex, complex, complex, complex]:
    """Matrice densité réduite ρ_q = Tr_reste(|ψ><ψ|) pour un qubit donné.

    Retourne (ρ00, ρ01, ρ10, ρ11).
    """
    pas = 1 << qubit
    r00 = r01 = r10 = r11 = 0j
    dim = 1 << nb_qubits
    for base in range(dim):
        if base & pas:
            continue
        i0, i1 = base, base | pas
        a0, a1 = etat[i0], etat[i1]
        r00 += a0 * a0.conjugate()
        r01 += a0 * a1.conjugate()
        r10 += a1 * a0.conjugate()
        r11 += a1 * a1.conjugate()
    return (r00, r01, r10, r11)


def vecteur_bloch(etat: Sequence[complex], nb_qubits: int,
                  qubit: int) -> Tuple[float, float, float]:
    """Vecteur de Bloch (x, y, z) du qubit : <X>, <Y>, <Z> sur ρ réduite."""
    r00, r01, r10, r11 = matrice_reduite(etat, nb_qubits, qubit)
    x = (r01 + r10).real
    y = (1j * (r01 - r10)).real
    z = (r00 - r11).real
    return (x, y, z)


def longueur_bloch(etat: Sequence[complex], nb_qubits: int,
                   qubit: int) -> float:
    """|r| ∈ [0 ; 1] : 1 = état pur local, <1 = qubit intriqué/mixte."""
    x, y, z = vecteur_bloch(etat, nb_qubits, qubit)
    return math.sqrt(x * x + y * y + z * z)


def concurrence_2q(etat: Sequence[complex]) -> float:
    """Concurrence exacte d'un état PUR à 2 qubits : C = 2|a00·a11 − a01·a10|."""
    if len(etat) != 4:
        raise ValueError("La concurrence 2q exige un vecteur de dimension 4")
    a00, a01, a10, a11 = etat
    return min(1.0, 2.0 * abs(a00 * a11 - a01 * a10))


def entropie_intrication_2q(etat: Sequence[complex]) -> float:
    """Entropie de von Neumann de ρ réduite (mesure d'intrication, 2 qubits purs)."""
    r00, r01, r10, _ = matrice_reduite(etat, 2, 0)
    # ρ réduite hermitienne 2×2 : λ± = (1 ± √((r00−r11)² + 4|r01|²)) / 2
    r11 = 1.0 - r00.real  # Tr ρ = 1 pour état pur normalisé
    delta = math.sqrt(max(0.0, (2 * r00.real - 1) ** 2 + 4 * abs(r01) ** 2))
    lam_plus = (1 + delta) / 2
    lam_moins = (1 - delta) / 2
    s = 0.0
    for lam in (lam_plus, lam_moins):
        if lam > 1e-15:
            s -= lam * math.log2(lam)
    return s


def metriques_completes(etat: Sequence[complex], nb_qubits: int) -> Dict[str, object]:
    """Bilan complet : Bloch par qubit + concurrence/entropie si n = 2."""
    res: Dict[str, object] = {
        "bloch": {
            f"q[{q}]": [round(v, 6) for v in vecteur_bloch(etat, nb_qubits, q)]
            for q in range(nb_qubits)
        },
        "purete_locale": {
            # Tr(ρ_q²) = (1 + |r|²)/2 ∈ [0.5 ; 1] — 1 = qubit pur, 0.5 = maximalement intriqué
            f"q[{q}]": round((1 + longueur_bloch(etat, nb_qubits, q) ** 2) / 2, 6)
            for q in range(nb_qubits)
        },
    }
    if nb_qubits == 2:
        res["concurrence"] = round(concurrence_2q(etat), 6)
        res["entropie_intrication_bits"] = round(entropie_intrication_2q(etat), 6)
    return res
