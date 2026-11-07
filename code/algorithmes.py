# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   ALGORITHMES AVANCÉS — VQE JOUET (H₂) & SHOR JOUET (N=15)
===============================================================================
Deux algorithmes quantiques emblématiques exécutés sur le noyau vecteur
d'état, honnêtement dimensionnés pour un émulateur pur Python :

  • VQE : hamiltonien H₂ à 2 qubits (mapping de parité, coefficients de la
    littérature STO-3G à R = 0.735 Å). Optimisation par recherche aléatoire
    d'un ansatz hardware-efficient — résultat comparé à l'énergie exacte
    calculée par diagonalisation (preuve de convergence, pas de magie).

  • SHOR : recherche de période de f(x) = a^x mod 15 par estimation de
    phase (QPE). La multiplication modulaire U_a est compilée en
    PERMUTATION des états de base — unitaire légitime du formalisme,
    appliquée directement au vecteur (registre comptage 3q + travail 4q).

Aucun de ces algorithmes ne « casse » quoi que ce soit : N=15, n≤7.
===============================================================================
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

from noyau_statevector import Operation, SimulateurVecteurEtat


# ---------------------------------------------------------------------------
# VQE — H₂ à 2 qubits
# ---------------------------------------------------------------------------

# Coefficients du hamiltonien H₂ (STO-3G, R = 0.735 Å, mapping parité,
# littérature : Whitfield et al. / tutoriels VQE usuels)
H2_COEFFS = {
    "II": -1.0524,
    "ZI": 0.3979,
    "IZ": -0.3979,
    "ZZ": -0.0113,
    "XX": 0.1809,
    "YY": 0.1809,
}


def _appliquer_pauli_terme(etat: Sequence[complex], terme: str,
                           n: int = 2) -> List[complex]:
    """Applique un produit de Pauli (chaîne 'ZI','XX',...) au vecteur 2-qubits.

    Convention : terme[0] agit sur q[1] (MSB), terme[1] sur q[0] (LSB),
    aligné sur l'écriture habituelle |q1 q0>.
    """
    sortie = [0j] * len(etat)
    for i, amp in enumerate(etat):
        if amp == 0:
            continue
        j, phase = i, 1 + 0j
        for k, lettre in enumerate(terme):
            q = len(terme) - 1 - k
            bit = (i >> q) & 1
            if lettre == "X":
                j ^= 1 << q
            elif lettre == "Y":
                j ^= 1 << q
                phase *= 1j if bit == 0 else -1j
            elif lettre == "Z":
                phase *= 1 if bit == 0 else -1
        sortie[j] += phase * amp
    return sortie


def esperance_hamiltonien(etat: Sequence[complex],
                          coeffs: Dict[str, float] = H2_COEFFS) -> float:
    """<ψ|H|ψ> exact pour un hamiltonien de Pauli à 2 qubits."""
    total = 0.0
    for terme, c in coeffs.items():
        image = _appliquer_pauli_terme(etat, terme)
        total += c * sum(a.conjugate() * b for a, b in zip(etat, image)).real
    return total


def energie_exacte_h2() -> float:
    """Énergie fondamentale exacte par construction de la matrice 4×4."""
    h = [[0j] * 4 for _ in range(4)]
    for j in range(4):
        colonne = [0j] * 4
        colonne[j] = 1 + 0j
        for terme, c in H2_COEFFS.items():
            image = _appliquer_pauli_terme(colonne, terme)
            for i in range(4):
                h[i][j] += c * image[i]
    # Jacobi sur la partie hermitienne
    a = [[h[i][j].real for j in range(4)] for i in range(4)]  # noqa: F841
    for _ in range(50):
        off = 0.0
        for p in range(4):
            for q in range(p + 1, 4):
                if abs(a[p][q]) > 1e-15:
                    off += a[p][q] ** 2
                    t = 0.5 * math.atan2(2 * a[p][q], a[q][q] - a[p][p])
                    c, s = math.cos(t), math.sin(t)
                    for k in range(4):
                        apk, aqk = a[p][k], a[q][k]
                        a[p][k], a[q][k] = c * apk - s * aqk, s * apk + c * aqk
                    for k in range(4):
                        akp, akq = a[k][p], a[k][q]
                        a[k][p], a[k][q] = c * akp - s * akq, s * akp + c * akq
                    a[p][q] = a[q][p] = 0.0
        if off < 1e-28:
            break
    return min(a[i][i] for i in range(4))


def _energie_ansatz(angles: Sequence[float]) -> float:
    """Énergie <ψ(θ)|H|ψ(θ)> de l'ansatz hardware-efficient à 4 paramètres."""
    sim = SimulateurVecteurEtat(2, graine=0)
    sim.executer([
        Operation("ry", (0,), (angles[0],)),
        Operation("cx", (0, 1)),
        Operation("ry", (1,), (angles[1],)),
        Operation("cx", (0, 1)),
        Operation("ry", (0,), (angles[2],)),
        Operation("ry", (1,), (angles[3],)),
    ])
    return esperance_hamiltonien(sim.etat)


def vqe_h2(essais: int = 400, graine: int = 20261107) -> Dict[str, object]:
    """Optimise l'ansatz : recherche aléatoire + descente de coordonnées."""
    rng = random.Random(graine)
    exacte = energie_exacte_h2()
    meilleur = {"energie": math.inf, "params": None}

    for _ in range(essais):
        angles = [rng.uniform(-math.pi, math.pi) for _ in range(4)]
        e = _energie_ansatz(angles)
        if e < meilleur["energie"]:
            meilleur = {"energie": e, "params": list(angles)}

    # Raffinement : descente de coordonnées autour du meilleur point
    params = meilleur["params"]
    pas = 0.4
    for _ in range(60):
        ameliore = False
        for k in range(4):
            for delta in (pas, -pas):
                candidat = list(params)
                candidat[k] += delta
                e = _energie_ansatz(candidat)
                if e < meilleur["energie"] - 1e-12:
                    meilleur = {"energie": e, "params": candidat}
                    params = candidat
                    ameliore = True
        if not ameliore:
            pas *= 0.5
            if pas < 1e-6:
                break

    ecart = abs(meilleur["energie"] - exacte)
    return {
        "algorithme": "VQE",
        "molecule": "H2 (STO-3G, R=0.735 Å, mapping parité, 2 qubits)",
        "hamiltonien": H2_COEFFS,
        "essais": essais,
        "ansatz_params_rad": [round(a, 4) for a in meilleur["params"]],
        "energie_vqe_ha": round(meilleur["energie"], 6),
        "energie_exacte_ha": round(exacte, 6),
        "ecart_mha": round(ecart * 1000, 4),
        "statut": "jouet pédagogique — pas une prédiction chimique de production",
    }


# ---------------------------------------------------------------------------
# SHOR — factorisation de 15 par recherche de période (QPE)
# ---------------------------------------------------------------------------

def _table_permutation_mod(a: int, n_mod: int, m_bits: int) -> Tuple[int, ...]:
    """Table de permutation v → (v·a) mod n sur m_bits qubits (v < n seulement)."""
    table = []
    for v in range(1 << m_bits):
        table.append((v * a) % n_mod if v < n_mod else v)
    return tuple(table)


def _ops_qft_inverse(qubits: Sequence[int]) -> List[Operation]:
    """QFT inverse = adjointe de la QFT directe (swaps puis phases négatives + H)."""
    ops: List[Operation] = []
    n = len(qubits)
    for i in range(n // 2):
        ops.append(Operation("swap", (qubits[i], qubits[n - 1 - i])))
    for i in reversed(range(n)):
        for k in reversed(range(i + 1, n)):
            ops.append(Operation("p", (qubits[i],),
                                 (-math.pi / (1 << (k - i)),), (qubits[k],)))
        ops.append(Operation("h", (qubits[i],)))
    return ops


def shor_factoriser(n_cible: int = 15, a: int = 7,
                    shots: int = 64, graine: int = 20261107) -> Dict[str, object]:
    """Factorise n par recherche de période de a^x mod n via QPE émulée."""
    if math.gcd(a, n_cible) != 1:
        p = math.gcd(a, n_cible)
        return {"facteurs": [p, n_cible // p], "note": "a partage un facteur avec N"}
    m_bits = max(4, (n_cible - 1).bit_length())
    # 3 bits de comptage suffisent pour les périodes ≤ 8
    nb_comptage = 3
    comptage = list(range(nb_comptage))
    travail = list(range(nb_comptage, nb_comptage + m_bits))
    nb_qubits = nb_comptage + m_bits

    ops: List[Operation] = [Operation("x", (travail[0],))]  # |1> : bit 0 de la valeur
    for q in comptage:
        ops.append(Operation("h", (q,)))
    for j, q in enumerate(comptage):
        puissance = pow(a, 1 << (nb_comptage - 1 - j), n_cible)
        table = _table_permutation_mod(puissance, n_cible, m_bits)
        ops.append(Operation("perm", tuple(travail), (), (q,), table))
    ops += _ops_qft_inverse(comptage)

    sim = SimulateurVecteurEtat(nb_qubits, graine=graine)
    sim.executer(ops)

    # Distribution du registre de comptage
    dist: Dict[int, float] = {}
    for i, amp in enumerate(sim.etat):
        p = abs(amp) ** 2
        if p > 1e-12:
            v_compt = i & ((1 << nb_comptage) - 1)
            dist[v_compt] = dist.get(v_compt, 0.0) + p

    # Phase → fraction continue → période candidate
    pics = sorted(dist.items(), key=lambda kv: -kv[1])[:4]
    periodes = set()
    for mesure, proba in pics:
        frac = Fraction(mesure, 1 << nb_comptage).limit_denominator(n_cible)
        if frac.denominator > 1:
            periodes.add(frac.denominator)

    facteurs: List[int] = []
    for r in sorted(periodes):
        if r % 2 == 0 and pow(a, r // 2, n_cible) != n_cible - 1:
            for cand in (math.gcd(pow(a, r // 2) - 1, n_cible),
                         math.gcd(pow(a, r // 2) + 1, n_cible)):
                if 1 < cand < n_cible and cand not in facteurs:
                    facteurs.append(cand)

    return {
        "algorithme": "SHOR (recherche de période, QPE)",
        "N": n_cible, "a": a,
        "nb_qubits": nb_qubits,
        "nb_portes": len(ops),
        "distribution_comptage": {
            format(k, f"0{nb_comptage}b"): round(v, 5)
            for k, v in sorted(dist.items())
        },
        "periodes_candidats": sorted(periodes),
        "facteurs": sorted(facteurs) or [1, n_cible],
        "statut": "démonstration jouet N=15 — aucune menace cryptographique réelle",
    }
