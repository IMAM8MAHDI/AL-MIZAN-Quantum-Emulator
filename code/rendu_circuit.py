# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   RENDU ASCII DE CIRCUIT — ÉMULATEUR QUANTIQUE AL-MIZAN
===============================================================================
Dessine un circuit en texte (style Qiskit text drawer, simplifié) :

     q[0] ──H────●─────────M──
                 │
     q[1] ──────⊕─────────M──

Les colonnes s'alignent par porte ; les liaisons contrôle→cible sont
matérialisées par des verticales « │ ».
===============================================================================
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

from noyau_statevector import Operation


def _etiquette(op: Operation) -> str:
    nom = op.nom.upper()
    if op.params:
        args = ",".join(f"{p:.3g}" for p in op.params)
        return f"{nom}({args})"
    return {"CX": "X", "CNOT": "X", "CZ": "Z", "CY": "Y", "CH": "H",
            "CCX": "X"}.get(nom, nom)


def dessiner_circuit(ops: Sequence[Operation], nb_qubits: int,
                     largeur_porte: int = 7) -> str:
    """Rend un circuit en ASCII. Retourne une chaîne multi-lignes."""
    nb_colonnes = max(1, len(ops))
    lignes: List[List[str]] = [
        [f"q[{q}] ", *(["─" * largeur_porte] * nb_colonnes)]
        for q in range(nb_qubits)
    ]

    for col, op in enumerate(ops):
        nom = op.nom.lower()
        if nom == "measure":
            for q in range(nb_qubits):
                lignes[q][col + 1] = "─M─".center(largeur_porte, "─")
            continue
        if nom == "reset":
            for q in op.cibles:
                lignes[q][col + 1] = "─|0>─".center(largeur_porte, "─")
            continue

        cibles = set(op.cibles)
        controles = set(op.controles)
        nom_l = op.nom.lower()
        if nom_l in ("cx", "cnot", "cz", "cy", "ch"):
            controles.add(op.cibles[0])
            cibles = {op.cibles[1]}
        elif nom_l == "ccx":
            controles.update(op.cibles[:2])
            cibles = {op.cibles[2]}
        elif nom_l == "swap":
            for q in op.cibles:
                lignes[q][col + 1] = "─✕─".center(largeur_porte, "─")
            lo, hi = min(op.cibles), max(op.cibles)
            for q in range(lo + 1, hi):
                lignes[q][col + 1] = "─│─".center(largeur_porte, "─")
            continue

        for q in controles:
            lignes[q][col + 1] = "─●─".center(largeur_porte, "─")
        for q in cibles:
            eti = _etiquette(op)
            symbole = "⊕" if nom_l in ("cx", "cnot", "ccx") else eti
            lignes[q][col + 1] = f"─{symbole}─".center(largeur_porte, "─")

        if controles and cibles:
            lo = min(min(controles), min(cibles))
            hi = max(max(controles), max(cibles))
            for q in range(lo + 1, hi):
                if q not in controles and q not in cibles:
                    lignes[q][col + 1] = "─│─".center(largeur_porte, "─")

    return "\n".join("".join(c for c in ligne) for ligne in lignes)
