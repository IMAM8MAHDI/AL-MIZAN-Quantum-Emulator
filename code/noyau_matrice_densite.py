# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   NOYAU MATRICE DENSITÉ — SIMULATION EXACTE DES ÉTATS MIXTES (ρ)
===============================================================================
Contrairement au vecteur d'état (états purs + bruit par trajectoires
stochastiques), la matrice densité ρ ∈ C^(2^n × 2^n) suit EXACTEMENT
l'évolution sous canaux de Kraus : dépolarisant, déphasage, amortissement
d'amplitude T1. Coût : O(16^n) par porte — limité à 8 qubits en pur Python.

Grandeurs exactes : pureté Tr(ρ²), fidélité <ψ|ρ|ψ>, entropie de von
Neumann S(ρ) via diagonalisation de Jacobi hermitienne.

Statut honnête : simulation classique exacte du modèle de bruit choisi —
pas une mesure de matériel réel.
===============================================================================
"""

from __future__ import annotations

import cmath
import math
from typing import Dict, List, Optional, Sequence, Tuple

from noyau_statevector import (
    ModeleBruit,
    Operation,
    _matrice_h,
    _matrice_identite,
    _matrice_p,
    _matrice_rx,
    _matrice_ry,
    _matrice_rz,
    _matrice_s,
    _matrice_sdg,
    _matrice_t,
    _matrice_tdg,
    _matrice_u,
    _matrice_x,
    _matrice_y,
    _matrice_z,
)

QUBITS_MAX_DENSITE = 8  # 256×256 complexes — limite confortable pur Python

_MATRICES_FIXES = {
    "id": _matrice_identite, "h": _matrice_h, "x": _matrice_x,
    "y": _matrice_y, "z": _matrice_z, "s": _matrice_s, "sdg": _matrice_sdg,
    "t": _matrice_t, "tdg": _matrice_tdg,
}


def _matrice_porte(nom: str, params: Sequence[float]) -> Tuple[complex, ...]:
    """Matrice 2×2 associée à une porte (lève ValueError si inconnue)."""
    if nom in _MATRICES_FIXES:
        return _MATRICES_FIXES[nom]()
    if nom in ("p", "u1"):
        return _matrice_p(params[0])
    if nom == "rx":
        return _matrice_rx(params[0])
    if nom == "ry":
        return _matrice_ry(params[0])
    if nom == "rz":
        return _matrice_rz(params[0])
    if nom in ("u", "u3"):
        return _matrice_u(params[0], params[1], params[2])
    if nom == "cx" or nom == "cnot":
        return _matrice_x()
    if nom == "cz":
        return _matrice_z()
    if nom == "cy":
        return _matrice_y()
    if nom == "ccx":
        return _matrice_x()
    if nom == "ch":
        return _matrice_h()
    raise ValueError(f"Porte inconnue pour la matrice densité : {nom!r}")


def _controles_de(nom: str, cibles: Sequence[int], controles: Sequence[int]) -> Tuple[int, ...]:
    """Toutes les lignes de contrôle effectives d'une opération."""
    nom = nom.lower()
    if nom in ("cx", "cnot", "cz", "cy", "ch"):
        return (*controles, cibles[0])
    if nom == "ccx":
        return (*controles, cibles[0], cibles[1])
    return tuple(controles)


def _cible_de(nom: str, cibles: Sequence[int]) -> int:
    nom = nom.lower()
    if nom == "ccx":
        return cibles[2]
    if nom in ("cx", "cnot", "cz", "cy", "ch"):
        return cibles[1]
    return cibles[0]


class SimulateurMatriceDensite:
    """ρ sur 2^n dimensions — évolution exacte par portes et canaux de Kraus."""

    def __init__(self, nb_qubits: int):
        if not 1 <= nb_qubits <= QUBITS_MAX_DENSITE:
            raise ValueError(
                f"nb_qubits doit être dans [1 ; {QUBITS_MAX_DENSITE}]")
        self.n = nb_qubits
        self.dim = 1 << nb_qubits
        # ρ stocké à plat, ligne-major : rho[i*dim + j]
        self.rho: List[complex] = [0j] * (self.dim * self.dim)
        self.rho[0] = 1 + 0j  # |0...0><0...0|

    # -- conjugaison unitaire ρ → U ρ U† ------------------------------------

    def _conjuguer_1q(self, u: Tuple[complex, ...], cible: int,
                      controles: Sequence[int] = ()) -> None:
        """ρ'[i,j] = Σ_ab A[i_t,a] ρ[i^a, j^b] conj(A[j_t,b])

        où A = U si les contrôles de l'indice sont tous à 1, sinon I.
        """
        dim, t = self.dim, cible
        masque_ctrl = 0
        for c in controles:
            masque_ctrl |= 1 << c
        pas = 1 << t
        nouveau = [0j] * (dim * dim)
        u10, u11 = u[2], u[3]

        for i in range(dim):
            ctrl_i = (i & masque_ctrl) == masque_ctrl
            bit_i = (i >> t) & 1
            i0 = i & ~pas
            for j in range(dim):
                ctrl_j = (j & masque_ctrl) == masque_ctrl
                bit_j = (j >> t) & 1
                j0 = j & ~pas
                # ρ'[i,j] = Σ_a A[i, a] (Σ_b ρ[a,b'] conj(A[j, b]))
                # indices a = bit t de i remplacé, b = bit t de j remplacé
                total = 0j
                for a in (0, 1):
                    coef_i = u[bit_i * 2 + a] if ctrl_i else (1.0 if a == bit_i else 0.0)
                    if coef_i == 0:
                        continue
                    ia = i0 | (a << t)
                    acc = 0j
                    for b in (0, 1):
                        coef_j = u[bit_j * 2 + b] if ctrl_j else (1.0 if b == bit_j else 0.0)
                        if coef_j == 0:
                            continue
                        jb = j0 | (b << t)
                        acc += self.rho[ia * dim + jb] * coef_j.conjugate()
                    total += coef_i * acc
                nouveau[i * dim + j] = total
        self.rho = nouveau

    def _conjuguer_swap(self, q1: int, q2: int) -> None:
        if q1 == q2:
            return
        dim = self.dim
        b1, b2 = 1 << q1, 1 << q2

        def ech(i: int) -> int:
            return ((i & ~b1 & ~b2)
                    | (((i >> q1) & 1) << q2)
                    | (((i >> q2) & 1) << q1))

        nouveau = [0j] * (dim * dim)
        for i in range(dim):
            ei = ech(i)
            for j in range(dim):
                nouveau[ei * dim + ech(j)] = self.rho[i * dim + j]
        self.rho = nouveau

    # -- canaux de Kraus -----------------------------------------------------

    def _kraus_amortissement(self, qubit: int, gamma: float) -> None:
        """Amortissement d'amplitude : K0=diag(1,√(1-γ)), K1=[[0,√γ],[0,0]]."""
        att = math.sqrt(1.0 - gamma)
        s = math.sqrt(gamma)
        self._appliquer_kraus(qubit,
                              ((1 + 0j, 0j, 0j, complex(att)),
                               (0j, complex(s), 0j, 0j)))

    def _kraus_depolarisant(self, qubit: int, p: float) -> None:
        """ρ → (1-p)ρ + p/3 (XρX + YρY + ZρZ) — bruit dépolarisant standard."""
        r = math.sqrt(p / 3.0)
        g = math.sqrt(1.0 - p)
        self._appliquer_kraus(qubit, (
            tuple(c * g for c in _matrice_identite()),
            tuple(c * r for c in _matrice_x()),
            tuple(c * r for c in _matrice_y()),
            tuple(c * r for c in _matrice_z()),
        ))

    def _appliquer_kraus(self, qubit: int,
                         kraus: Sequence[Tuple[complex, ...]]) -> None:
        """ρ → Σ_k K_k ρ K_k† pour un canal agissant sur un seul qubit."""
        dim, t = self.dim, qubit
        pas = 1 << t
        nouveau = [0j] * (dim * dim)
        for k in kraus:
            for i in range(dim):
                bit_i = (i >> t) & 1
                i0 = i & ~pas
                for a in (0, 1):
                    coef_i = k[bit_i * 2 + a]
                    if coef_i == 0:
                        continue
                    ia = i0 | (a << t)
                    for j in range(dim):
                        bit_j = (j >> t) & 1
                        j0 = j & ~pas
                        acc = 0j
                        for b in (0, 1):
                            coef_j = k[bit_j * 2 + b]
                            if coef_j == 0:
                                continue
                            jb = j0 | (b << t)
                            acc += self.rho[ia * dim + jb] * coef_j.conjugate()
                        if acc:
                            nouveau[i * dim + j] += coef_i * acc
        self.rho = nouveau

    # -- exécution ------------------------------------------------------------

    def porte(self, op: Operation, bruit: Optional[ModeleBruit] = None,
              dephasage: float = 0.0) -> None:
        nom = op.nom.lower()
        if nom in ("id", "barrier"):
            return
        if nom == "measure":
            return  # la mesure est traitée par probabilites_mesure
        if nom == "reset":
            self._reset(op.cibles[0])
            return
        if nom == "swap":
            self._conjuguer_swap(op.cibles[0], op.cibles[1])
        else:
            u = _matrice_porte(nom, op.params)
            cible = _cible_de(nom, op.cibles)
            controles = _controles_de(nom, op.cibles, op.controles)
            self._conjuguer_1q(u, cible, controles)
            if bruit is not None:
                if bruit.p_depolarisant > 0.0:
                    self._kraus_depolarisant(cible, bruit.p_depolarisant)
                if bruit.gamma_amortissement > 0.0:
                    self._kraus_amortissement(cible, bruit.gamma_amortissement)
                if dephasage > 0.0:
                    r = math.sqrt(dephasage / 2.0)
                    g = math.sqrt(1.0 - dephasage / 2.0)
                    self._appliquer_kraus(cible, (
                        tuple(c * g for c in _matrice_identite()),
                        tuple(c * r for c in _matrice_z()),
                    ))

    def _reset(self, qubit: int) -> None:
        """Projection sur |0> du qubit (canal de réinitialisation)."""
        self._appliquer_kraus(qubit, (
            (1 + 0j, 0j, 0j, 0j),   # |0><0|
            (0j, 1 + 0j, 0j, 0j),   # |0><1|
        ))

    def executer(self, ops: Sequence[Operation],
                 bruit: Optional[ModeleBruit] = None,
                 dephasage: float = 0.0) -> None:
        for op in ops:
            self.porte(op, bruit, dephasage)

    # -- observables ----------------------------------------------------------

    def probabilites_mesure(self) -> Dict[int, float]:
        """Diagonale de ρ : probabilités EXACTES de chaque bitstring."""
        dim = self.dim
        return {i: max(0.0, self.rho[i * dim + i].real)
                for i in range(dim) if self.rho[i * dim + i].real > 1e-15}

    def purete(self) -> float:
        """Tr(ρ²) ∈ [1/dim ; 1]."""
        dim = self.dim
        total = 0.0
        for i in range(dim):
            for j in range(dim):
                total += (self.rho[i * dim + j] * self.rho[j * dim + i]).real
        return total

    def fidelite_etat_pur(self, vecteur: Sequence[complex]) -> float:
        """<ψ|ρ|ψ> — fidélité avec un état pur de même dimension."""
        dim = self.dim
        total = 0j
        for i in range(dim):
            vi = vecteur[i].conjugate()
            if vi == 0:
                continue
            for j in range(dim):
                total += vi * self.rho[i * dim + j] * vecteur[j]
        return max(0.0, min(1.0, total.real))

    def valeurs_propres(self) -> List[float]:
        """Spectre d'une matrice hermitienne par rotations unitaires de Jacobi.

        Les cohérences imaginaires comptent : S, T et les rotations d'axe X ou
        Y engendrent des termes hors diagonale purement imaginaires. Diagonaliser
        la seule partie réelle les jetait — sur ρ = |+i⟩⟨+i| =
        [[1/2, i/2], [-i/2, 1/2]] l'ancienne version rendait {1/2, 1/2} et donc
        1 bit d'entropie pour un état pur, alors que le spectre exact est
        {1, 0} et S = 0.

        Chaque pivot (p, q) subit deux transformations unitaires : une mise en
        phase qui rend le pivot réel positif sans toucher la diagonale, puis la
        rotation réelle de Jacobi. stdlib uniquement, O(dim²) paires × O(dim)
        par paire, dim = 2**nb_qubits.
        """
        dim = self.dim
        a = [complex(self.rho[i * dim + j]) for i in range(dim) for j in range(dim)]

        def norm_hors_diag() -> float:
            return sum(abs(a[p * dim + q]) ** 2
                       for p in range(dim) for q in range(p + 1, dim))

        def rot(p: int, q: int, module: complex) -> None:
            # (1) U†AU avec U = diag(…, 1, u_q, …) : le pivot devient réel
            #     positif, la diagonale est invariée (u puis ū sur a[q][q]).
            u = module.conjugate() / abs(module)
            for k in range(dim):
                a[k * dim + q] *= u
                a[q * dim + k] *= u.conjugate()
            # (2) rotation réelle A ← R A Rᵀ dans le plan (p, q).
            app = a[p * dim + p].real
            aqq = a[q * dim + q].real
            theta = 0.5 * math.atan2(2 * abs(module), aqq - app)
            c, s = math.cos(theta), math.sin(theta)
            for k in range(dim):
                apk, aqk = a[p * dim + k], a[q * dim + k]
                a[p * dim + k] = c * apk - s * aqk
                a[q * dim + k] = s * apk + c * aqk
            for k in range(dim):
                akp, akq = a[k * dim + p], a[k * dim + q]
                a[k * dim + p] = c * akp - s * akq
                a[k * dim + q] = s * akp + c * akq
            a[p * dim + q] = 0j
            a[q * dim + p] = 0j

        depart = norm_hors_diag()
        if depart == 0.0:
            return [self.rho[i * dim + i].real for i in range(dim)]
        for _ in range(60):  # balayages cycliques
            if norm_hors_diag() <= max(1e-30, depart * 1e-26):
                break
            for p in range(dim):
                for q in range(p + 1, dim):
                    apq = a[p * dim + q]
                    if abs(apq) > 1e-16:
                        rot(p, q, apq)
        return [a[i * dim + i].real for i in range(dim)]

    def entropie_von_neumann(self) -> float:
        """S(ρ) = −Tr(ρ log₂ ρ) en bits — spectre hermitien complexe exact."""
        s = 0.0
        for lam in self.valeurs_propres():
            if lam > 1e-12:
                s -= lam * math.log2(lam)
        return s


def comparer_vecteur_densite(ops: Sequence[Operation], nb_qubits: int,
                             bruit: Optional[ModeleBruit] = None,
                             dephasage: float = 0.0) -> Dict[str, object]:
    """Exécute le circuit en vecteur (idéal) et en densité (bruité exact)."""
    ops_sans_mesure = [op for op in ops if op.nom != "measure"]

    ideal = None
    try:
        from noyau_statevector import SimulateurVecteurEtat
        ideal = SimulateurVecteurEtat(nb_qubits, graine=0)
        ideal.executer(ops_sans_mesure)
    except Exception:
        ideal = None

    sim = SimulateurMatriceDensite(nb_qubits)
    sim.executer(ops_sans_mesure, bruit, dephasage)

    resultat: Dict[str, object] = {
        "probabilites_exactes": {
            format(i, f"0{nb_qubits}b"): round(p, 8)
            for i, p in sorted(sim.probabilites_mesure().items())
        },
        "purete_tr_rho2": round(sim.purete(), 8),
        "entropie_von_neumann_bits": round(sim.entropie_von_neumann(), 8),
    }
    if ideal is not None and ideal.dim == sim.dim:
        resultat["fidelite_vs_ideal"] = round(sim.fidelite_etat_pur(ideal.etat), 8)
    return resultat
