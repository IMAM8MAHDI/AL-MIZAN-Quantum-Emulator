# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2026 IMAM8MAHDI / Astro-Code Ecosystem
# SPDX-License-Identifier: GPL-3.0-only OR AGPL-3.0-only
"""
===============================================================================
   NOYAU VECTEUR D'ÉTAT — ÉMULATEUR QUANTIQUE AL-MIZAN (pur Python, 2^n exact)
===============================================================================
Simulateur à vecteur d'état généraliste : n qubits, amplitudes complexes,
jeu de portes complet, mesures de Born (tirs) et injection de bruit par
trajectoires quantiques (dépolarisant + amortissement d'amplitude).

Convention : q[i] = bit i de l'indice (little-endian, convention Qiskit).
Les chaînes de bits affichées sont MSB→LSB : q[n-1]...q[1]q[0].

Statut honnête : émulation classique de la mécanique quantique.
Coût mémoire/temps exponentiel en 2^n — aucun QPU réel n'est utilisé.
===============================================================================
"""

from __future__ import annotations

import cmath
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

QUBITS_MAX = 16  # 2^16 amplitudes = limite raisonnable en pur Python

RAC2_INV = 1.0 / math.sqrt(2.0)


# ---------------------------------------------------------------------------
# Matrices 2x2 des portes élémentaires ((a,b),(c,d)) — ligne-major
# ---------------------------------------------------------------------------

def _matrice_identite() -> Tuple[complex, complex, complex, complex]:
    return (1 + 0j, 0j, 0j, 1 + 0j)


def _matrice_h() -> Tuple[complex, complex, complex, complex]:
    return (RAC2_INV, RAC2_INV, RAC2_INV, -RAC2_INV)


def _matrice_x() -> Tuple[complex, complex, complex, complex]:
    return (0j, 1 + 0j, 1 + 0j, 0j)


def _matrice_y() -> Tuple[complex, complex, complex, complex]:
    return (0j, -1j, 1j, 0j)


def _matrice_z() -> Tuple[complex, complex, complex, complex]:
    return (1 + 0j, 0j, 0j, -1 + 0j)


def _matrice_s() -> Tuple[complex, complex, complex, complex]:
    return (1 + 0j, 0j, 0j, 1j)


def _matrice_sdg() -> Tuple[complex, complex, complex, complex]:
    return (1 + 0j, 0j, 0j, -1j)


def _matrice_t() -> Tuple[complex, complex, complex, complex]:
    return (1 + 0j, 0j, 0j, cmath.exp(1j * math.pi / 4))


def _matrice_tdg() -> Tuple[complex, complex, complex, complex]:
    return (1 + 0j, 0j, 0j, cmath.exp(-1j * math.pi / 4))


def _matrice_p(phi: float) -> Tuple[complex, complex, complex, complex]:
    return (1 + 0j, 0j, 0j, cmath.exp(1j * phi))


def _matrice_rx(theta: float) -> Tuple[complex, complex, complex, complex]:
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return (complex(c), -1j * s, -1j * s, complex(c))


def _matrice_ry(theta: float) -> Tuple[complex, complex, complex, complex]:
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return (complex(c), complex(-s), complex(s), complex(c))


def _matrice_rz(phi: float) -> Tuple[complex, complex, complex, complex]:
    return (cmath.exp(-1j * phi / 2), 0j, 0j, cmath.exp(1j * phi / 2))


def _matrice_u(theta: float, phi: float, lam: float) -> Tuple[complex, complex, complex, complex]:
    """Porte U(θ,φ,λ) OpenQASM 2.0."""
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return (
        complex(c),
        -cmath.exp(1j * lam) * s,
        cmath.exp(1j * phi) * s,
        cmath.exp(1j * (phi + lam)) * c,
    )


# ---------------------------------------------------------------------------
# Opérations du circuit
# ---------------------------------------------------------------------------

@dataclass
class Operation:
    """Une instruction du circuit : porte + cibles + contrôles + paramètre.

    `permutation` (optionnel) : table de permutation des états de base des
    qubits cibles — unitaire légitime utilisée p.ex. pour l'arithmétique
    modulaire de Shor (multiplication mod N compilée en permutation).
    """
    nom: str
    cibles: Tuple[int, ...]
    params: Tuple[float, ...] = ()
    controles: Tuple[int, ...] = ()
    permutation: Optional[Tuple[int, ...]] = None


@dataclass
class ModeleBruit:
    """Bruit par trajectoire : dépolarisant (p) et amortissement T1 (gamma)."""
    p_depolarisant: float = 0.0
    gamma_amortissement: float = 0.0

    @property
    def actif(self) -> bool:
        return self.p_depolarisant > 0.0 or self.gamma_amortissement > 0.0


class SimulateurVecteurEtat:
    """Vecteur d'état pur |ψ> ∈ C^(2^n), exécution exacte + bruit stochastique."""

    def __init__(self, nb_qubits: int, graine: Optional[int] = None):
        if not 1 <= nb_qubits <= QUBITS_MAX:
            raise ValueError(f"nb_qubits doit être dans [1 ; {QUBITS_MAX}]")
        self.n = nb_qubits
        self.dim = 1 << nb_qubits
        self.rng = random.Random(graine)
        self.etat: List[complex] = [0j] * self.dim
        self.etat[0] = 1 + 0j
        self.historique_mesures: List[Tuple[int, int]] = []

    # -- utilitaires --------------------------------------------------------

    def _verifier_qubit(self, *qs: int) -> None:
        for q in qs:
            if not 0 <= q < self.n:
                raise ValueError(f"Qubit {q} hors registre [0 ; {self.n})")

    def _appliquer_1q(self, mat: Tuple[complex, complex, complex, complex],
                      cible: int, controles: Sequence[int] = ()) -> None:
        """Applique une matrice 2×2 sur `cible`, conditionnée aux `controles` = 1."""
        self._verifier_qubit(cible, *controles)
        masque_ctrl = 0
        for c in controles:
            masque_ctrl |= 1 << c
        pas = 1 << cible
        a, b, c, d = mat
        for base in range(self.dim):
            if base & pas:
                continue
            if masque_ctrl and (base & masque_ctrl) != masque_ctrl:
                continue
            i0, i1 = base, base | pas
            a0, a1 = self.etat[i0], self.etat[i1]
            self.etat[i0] = a * a0 + b * a1
            self.etat[i1] = c * a0 + d * a1

    def _appliquer_permutation(self, perm: Sequence[int], cibles: Sequence[int],
                               controles: Sequence[int] = ()) -> None:
        """Permutation des états de base sur `cibles` (bijection), contrôlée.

        perm[v] = nouvelle valeur du registre cible quand il vaut v.
        """
        self._verifier_qubit(*cibles, *controles)
        if set(cibles) & set(controles):
            raise ValueError("Chevauchement cibles/contrôles dans la permutation")
        m = len(cibles)
        if len(perm) != (1 << m):
            raise ValueError("La permutation doit couvrir 2^m valeurs")
        masque_ctrl = 0
        for c in controles:
            masque_ctrl |= 1 << c
        nouveau = self.etat[:]
        bits_cibles = list(cibles)
        for i in range(self.dim):
            if masque_ctrl and (i & masque_ctrl) != masque_ctrl:
                continue
            v = 0
            for k, b in enumerate(bits_cibles):
                v |= ((i >> b) & 1) << k
            v2 = perm[v]
            if v2 == v:
                continue
            j = i
            for k, b in enumerate(bits_cibles):
                if (v2 >> k) & 1:
                    j |= 1 << b
                else:
                    j &= ~(1 << b)
            nouveau[j] = self.etat[i]
        self.etat = nouveau

    def _appliquer_swap(self, q1: int, q2: int) -> None:
        self._verifier_qubit(q1, q2)
        if q1 == q2:
            return
        b1, b2 = 1 << q1, 1 << q2
        for i in range(self.dim):
            bit1, bit2 = (i >> q1) & 1, (i >> q2) & 1
            if bit1 == 0 and bit2 == 1:
                j = (i | b1) & ~b2
                self.etat[i], self.etat[j] = self.etat[j], self.etat[i]

    def _normaliser(self) -> None:
        norme = math.sqrt(sum(abs(a) ** 2 for a in self.etat))
        if norme > 0:
            self.etat = [a / norme for a in self.etat]

    # -- portes publiques ---------------------------------------------------

    def porte(self, nom: str, cibles: Sequence[int],
              params: Sequence[float] = (), controles: Sequence[int] = ()) -> None:
        """Applique une porte nommée (h x y z s sdg t tdg p rx ry rz u cx cz cy swap ccx)."""
        nom = nom.lower()
        c = tuple(controles)
        if nom == "id" or nom == "barrier":
            return
        if nom == "h":
            self._appliquer_1q(_matrice_h(), cibles[0], c)
        elif nom == "x":
            self._appliquer_1q(_matrice_x(), cibles[0], c)
        elif nom == "y":
            self._appliquer_1q(_matrice_y(), cibles[0], c)
        elif nom == "z":
            self._appliquer_1q(_matrice_z(), cibles[0], c)
        elif nom == "s":
            self._appliquer_1q(_matrice_s(), cibles[0], c)
        elif nom == "sdg":
            self._appliquer_1q(_matrice_sdg(), cibles[0], c)
        elif nom == "t":
            self._appliquer_1q(_matrice_t(), cibles[0], c)
        elif nom == "tdg":
            self._appliquer_1q(_matrice_tdg(), cibles[0], c)
        elif nom in ("p", "u1"):
            self._appliquer_1q(_matrice_p(params[0]), cibles[0], c)
        elif nom == "rx":
            self._appliquer_1q(_matrice_rx(params[0]), cibles[0], c)
        elif nom == "ry":
            self._appliquer_1q(_matrice_ry(params[0]), cibles[0], c)
        elif nom == "rz":
            self._appliquer_1q(_matrice_rz(params[0]), cibles[0], c)
        elif nom in ("u", "u3"):
            self._appliquer_1q(_matrice_u(params[0], params[1], params[2]), cibles[0], c)
        elif nom == "cx" or nom == "cnot":
            self._appliquer_1q(_matrice_x(), cibles[1], (*c, cibles[0]))
        elif nom == "cz":
            self._appliquer_1q(_matrice_z(), cibles[1], (*c, cibles[0]))
        elif nom == "cy":
            self._appliquer_1q(_matrice_y(), cibles[1], (*c, cibles[0]))
        elif nom == "swap":
            self._appliquer_swap(cibles[0], cibles[1])
        elif nom == "ccx":
            self._appliquer_1q(_matrice_x(), cibles[2], (*c, cibles[0], cibles[1]))
        else:
            raise ValueError(f"Porte inconnue : {nom!r}")

    def reset(self, qubit: int) -> None:
        """Replace un qubit dans |0> (mesure + correction X conditionnelle)."""
        if self.mesurer_qubit(qubit) == 1:
            self._appliquer_1q(_matrice_x(), qubit)

    # -- bruit par trajectoire ----------------------------------------------

    def _bruit_1q(self, qubit: int, bruit: ModeleBruit) -> None:
        if bruit.gamma_amortissement > 0.0:
            g = bruit.gamma_amortissement
            # Canaux de Kraus : K0 = diag(1, √(1-γ)), K1 = [[0,√γ],[0,0]]
            pas = 1 << qubit
            p_emission = sum(abs(self.etat[i]) ** 2 for i in range(self.dim) if i & pas) * g
            if self.rng.random() < p_emission:
                for i in range(self.dim):
                    if i & pas:
                        self.etat[i & ~pas] += self.etat[i]
                        self.etat[i] = 0j
            else:
                att = math.sqrt(1.0 - g)
                for i in range(self.dim):
                    if i & pas:
                        self.etat[i] *= att
            self._normaliser()
        if bruit.p_depolarisant > 0.0 and self.rng.random() < bruit.p_depolarisant:
            pauli = self.rng.choice((_matrice_x, _matrice_y, _matrice_z))
            self._appliquer_1q(pauli(), qubit)

    # -- mesures ------------------------------------------------------------

    def probabilite_1(self, qubit: int) -> float:
        bit = 1 << qubit
        return sum(abs(self.etat[i]) ** 2 for i in range(self.dim) if i & bit)

    def mesurer_qubit(self, qubit: int) -> int:
        """Mesure de Born d'un qubit + effondrement du vecteur."""
        p1 = self.probabilite_1(qubit)
        resultat = 1 if self.rng.random() < p1 else 0
        bit = 1 << qubit
        reste = 0.0
        for i in range(self.dim):
            if ((i & bit) != 0) != bool(resultat):
                self.etat[i] = 0j
            else:
                reste += abs(self.etat[i]) ** 2
        if reste > 0:
            inv = 1.0 / math.sqrt(reste)
            for i in range(self.dim):
                if ((i & bit) != 0) == bool(resultat):
                    self.etat[i] *= inv
        self.historique_mesures.append((qubit, resultat))
        return resultat

    def mesurer_tout(self) -> int:
        """Tir de Born sur l'ensemble du registre (sans effondrement)."""
        x = self.rng.random()
        cumul = 0.0
        for i, a in enumerate(self.etat):
            cumul += abs(a) ** 2
            if x <= cumul:
                return i
        return self.dim - 1

    def probabilites(self) -> Dict[int, float]:
        return {i: abs(a) ** 2 for i, a in enumerate(self.etat) if abs(a) ** 2 > 1e-15}

    def esperance_z(self, qubit: int) -> float:
        """<Z_q> = P(0) − P(1) ∈ [-1 ; +1]."""
        return 1.0 - 2.0 * self.probabilite_1(qubit)

    def entropie_distribution(self) -> float:
        """Entropie de Shannon (bits) de la distribution de mesure — pure info."""
        h = 0.0
        for a in self.etat:
            p = abs(a) ** 2
            if p > 1e-15:
                h -= p * math.log2(p)
        return h

    def fidelite(self, autre: "SimulateurVecteurEtat") -> float:
        """Fidélité |<ψ|φ>|² entre deux états purs de même registre."""
        if autre.dim != self.dim:
            raise ValueError("Registres de tailles différentes")
        prod = sum(a.conjugate() * b for a, b in zip(self.etat, autre.etat))
        return abs(prod) ** 2

    # -- exécution de circuit -----------------------------------------------

    def executer(self, ops: Sequence[Operation], bruit: Optional[ModeleBruit] = None) -> None:
        """Exécute une liste d'opérations (bruit injecté après chaque porte)."""
        for op in ops:
            if op.nom == "measure":
                for q in op.cibles:
                    self.mesurer_qubit(q)
            elif op.nom == "reset":
                for q in op.cibles:
                    self.reset(q)
            elif op.nom == "perm":
                if op.permutation is None:
                    raise ValueError("Opération 'perm' sans table de permutation")
                self._appliquer_permutation(op.permutation, op.cibles, op.controles)
            else:
                self.porte(op.nom, op.cibles, op.params, op.controles)
                if bruit is not None and bruit.actif:
                    for q in op.cibles:
                        self._bruit_1q(q, bruit)


def executer_counts(ops: Sequence[Operation], nb_qubits: int, shots: int,
                    bruit: Optional[ModeleBruit] = None,
                    graine: Optional[int] = None) -> Dict[str, int]:
    """Exécute le circuit `shots` fois (trajectoires indépendantes) → histogramme.

    Les opérations `measure` structurelles sont ignorées : chaque trajectoire
    se termine par un tir de Born global. Convention bitstring MSB→LSB.
    """
    ops_sans_mesure = [op for op in ops if op.nom != "measure"]
    counts: Dict[str, int] = {}
    for tir in range(shots):
        sim = SimulateurVecteurEtat(nb_qubits,
                                    graine=None if graine is None else graine + tir)
        sim.executer(ops_sans_mesure, bruit)
        indice = sim.mesurer_tout()
        cle = format(indice, f"0{nb_qubits}b")
        counts[cle] = counts.get(cle, 0) + 1
    return counts


def distribution_depuis_counts(counts: Dict[str, int]) -> Dict[str, float]:
    """Convertit un histogramme {bitstring: n} en {|ket> : p} pour le transducteur."""
    total = sum(counts.values()) or 1
    return {f"|{k}>": v / total for k, v in counts.items()}
