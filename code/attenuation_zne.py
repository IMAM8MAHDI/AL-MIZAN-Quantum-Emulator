# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   ATTÉNUATION D'ERREUR PAR EXTRAPOLATION À BRUIT NUL (ZNE) — AL-MIZAN
===============================================================================
Principe : exécuter le même circuit à plusieurs niveaux de bruit amplifié
(facteurs d'échelle λ = 1, 2, 3 → p_eff = min(λ·p, 1)), mesurer une observable
(ex. <Z> d'un qubit ou probabilité d'un état cible), puis extrapoler
linéairement (Richardson) vers λ = 0 — le résultat « bruit nul » estimé.

C'est une atténuation logicielle honnête : elle réduit le biais statistique,
pas le bruit réel. Aucun matériel n'est impliqué.
===============================================================================
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from noyau_statevector import ModeleBruit, Operation, SimulateurVecteurEtat


@dataclass
class PointZne:
    facteur_echelle: float
    p_effectif: float
    observable: float
    shots: int


def _observable_counts(ops: Sequence[Operation], nb_qubits: int, shots: int,
                       bruit: ModeleBruit, graine: Optional[int],
                       qubit_observable: int) -> float:
    """Estime <Z> du qubit observable par trajectoires Monte Carlo."""
    ops_sans_mesure = [op for op in ops if op.nom != "measure"]
    total = 0.0
    for tir in range(shots):
        sim = SimulateurVecteurEtat(
            nb_qubits, graine=None if graine is None else graine + tir)
        sim.executer(ops_sans_mesure, bruit)
        total += 1.0 if sim.mesurer_tout() & (1 << qubit_observable) == 0 else -1.0
    return total / shots


def extrapolation_richardson(points: Sequence[PointZne]) -> Optional[float]:
    """Extrapolation linéaire moindres carrés vers λ=0."""
    n = len(points)
    if n < 2:
        return None
    sx = sum(p.facteur_echelle for p in points)
    sy = sum(p.observable for p in points)
    sxx = sum(p.facteur_echelle ** 2 for p in points)
    sxy = sum(p.facteur_echelle * p.observable for p in points)
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-15:
        return sy / n
    # f(0) = (Σy·Σx² − Σx·Σxy) / (n·Σx² − (Σx)²)
    return (sy * sxx - sx * sxy) / denom


def executer_zne(ops: Sequence[Operation], nb_qubits: int,
                 p_depolarisant: float,
                 echelles: Sequence[float] = (1.0, 2.0, 3.0),
                 shots_par_echelle: int = 256,
                 qubit_observable: int = 0,
                 gamma_amortissement: float = 0.0,
                 graine: Optional[int] = 20261107) -> Dict[str, object]:
    """ZNE complet : retourne les points mesurés et l'observable extrapolée à bruit nul."""
    if not 0 <= qubit_observable < nb_qubits:
        raise ValueError("qubit_observable hors registre")

    points: List[PointZne] = []
    for lam in echelles:
        bruit = ModeleBruit(
            p_depolarisant=min(1.0, p_depolarisant * lam),
            gamma_amortissement=min(1.0, gamma_amortissement * lam),
        )
        obs = _observable_counts(ops, nb_qubits, shots_par_echelle, bruit,
                                 graine=None if graine is None else graine + int(lam * 1000),
                                 qubit_observable=qubit_observable)
        points.append(PointZne(lam, bruit.p_depolarisant, obs, shots_par_echelle))

    extrapole = extrapolation_richardson(points)
    return {
        "methode": "ZNE / Richardson linéaire",
        "qubit_observable": qubit_observable,
        "points": [
            {"lambda": p.facteur_echelle, "p_eff": p.p_effectif,
             "observable_Z": round(p.observable, 6), "shots": p.shots}
            for p in points
        ],
        "observable_mesuree_lambda1": round(points[0].observable, 6),
        "observable_extrapolee_bruit_nul": None if extrapole is None else round(extrapole, 6),
        "note": "atténuation statistique du biais — le bruit réel n'est pas supprimé",
    }
